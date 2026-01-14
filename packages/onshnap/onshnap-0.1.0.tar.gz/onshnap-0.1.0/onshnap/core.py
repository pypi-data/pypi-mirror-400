"""Core logic for exporting Onshape assemblies to frozen-snapshot URDF."""

import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Self, TypedDict, cast

import numpy as np

from .client import DocumentInfo, OnshapeClient
from .utils import matrix_to_rpy, sanitize_name

logger = logging.getLogger(__name__)


OutputFormat = Literal["urdf", "mjcf"]


class OccurrenceDict(TypedDict, total=False):
    """Type definition for an occurrence from the Onshape API."""

    path: list[str]
    transform: list[float]  # 16 floats for 4x4 matrix
    hidden: bool
    fixed: bool


class InstanceDict(TypedDict, total=False):
    """Type definition for an instance in the assembly."""

    id: str
    documentId: str
    elementId: str
    partId: str
    name: str
    type: str  # "Part" or "Assembly"
    configuration: str


class PartDict(TypedDict, total=False):
    """Type definition for a part in the assembly."""

    documentId: str
    elementId: str
    partId: str
    name: str


class RootAssemblyDict(TypedDict, total=False):
    """Type definition for rootAssembly in the assembly response."""

    instances: list[InstanceDict]
    occurrences: list[OccurrenceDict]


class SubAssemblyDict(TypedDict, total=False):
    """Type definition for a subassembly in the assembly response."""

    instances: list[InstanceDict]


class AssemblyDict(TypedDict, total=False):
    """Type definition for the assembly API response."""

    rootAssembly: RootAssemblyDict
    subAssemblies: list[SubAssemblyDict]
    parts: list[PartDict]


@dataclass
class ExportConfig:
    """Configuration for export.

    Attributes:
        url: Onshape document URL
        output_dir: Directory to save output files
        mesh_dir: Subdirectory name for mesh files
        output_name: Base name for output files (without extension)
        units: Units for mesh export ("meter" or "inch")
        filetype: Output format ("urdf" or "mjcf")
    """

    url: str
    output_dir: Path = field(default_factory=lambda: Path("."))
    mesh_dir: str = "meshes"
    output_name: str = "onshnap"
    units: str = "meter"
    filetype: OutputFormat = "urdf"

    @classmethod
    def from_json(cls, path: Path) -> Self:
        """Load configuration from a JSON file."""
        with open(path) as f:
            data = json.load(f)

        filetype = data.get("filetype", "urdf")
        if filetype not in OutputFormat.__args__:  # type: ignore[attr-defined]
            raise ValueError(f"Invalid filetype: {filetype}. Must be one of: {OutputFormat}")

        return cls(
            url=data["url"],
            output_dir=path.parent,
            mesh_dir=data.get("mesh_dir", "meshes"),
            output_name=data.get("output_name", "onshnap"),
            units=data.get("units", "meter"),
            filetype=filetype,
        )


@dataclass
class PartOccurrence:
    """Represents a single part occurrence in the assembly."""

    # Path in the assembly tree (list of instance IDs)
    path: list[str]

    # The 4x4 world transform (row-major, 16 floats)
    transform: np.ndarray  # 4x4 matrix

    # Part identification
    document_id: str
    element_id: str
    part_id: str

    # Workspace info for downloading
    workspace_type: str
    workspace_id: str

    # Part name (for URDF link naming)
    name: str

    # Configuration string (if any)
    configuration: str = ""

    # Color (RGBA, 0-255 range)
    color: tuple[int, int, int, int] | None = None

    # Mass in kg (None if not available)
    mass: float | None = None

    # Center of mass in part frame (x, y, z) in meters
    center_of_mass: tuple[float, float, float] | None = None

    # Inertia matrix (3x3) in part frame, kg*m²
    # Stored as 9-element list [Ixx, Ixy, Ixz, Iyx, Iyy, Iyz, Izx, Izy, Izz]
    inertia: list[float] | None = None

    # Enumeration number (1-based) for duplicate names, None if unique
    enumeration: int | None = None

    @property
    def link_name(self) -> str:
        """Generate a sanitized link name for URDF."""
        if self.enumeration is not None:
            return sanitize_name(f"link_{self.name}_{self.enumeration}")
        return sanitize_name(f"link_{self.name}")

    @property
    def mesh_filename(self) -> str:
        """Generate a sanitized mesh filename."""
        if self.enumeration is not None:
            return sanitize_name(f"{self.name}_{self.enumeration}") + ".stl"
        return sanitize_name(f"{self.name}") + ".stl"


def parse_occurrences(
    occurrences: list[OccurrenceDict],
    assembly: AssemblyDict,
    doc: DocumentInfo,
    client: OnshapeClient | None = None,
) -> list[PartOccurrence]:
    """Parse occurrence data from the API into PartOccurrence objects.

    Args:
        occurrences: Raw occurrences from the API
        assembly: Assembly definition (for part metadata)
        doc: Document information
        client: Optional Onshape client for fetching part colors from metadata

    Returns:
        List of PartOccurrence objects
    """
    # Build a map from part path to part info
    # We need the assembly data to get part names and element IDs

    # First, build instance map from rootAssembly
    instance_map: dict[str, InstanceDict] = {}
    root_asm = assembly.get("rootAssembly", {})

    for instance in root_asm.get("instances", []):
        instance_map[instance["id"]] = instance

    # Also check subassemblies
    for sub in assembly.get("subAssemblies", []):
        for instance in sub.get("instances", []):
            instance_map[instance["id"]] = instance

    # Map from documentId+elementId+partId to Part info
    part_map: dict[tuple[str, str, str], PartDict] = {}
    for part in assembly.get("parts", []):
        key = (part["documentId"], part["elementId"], part["partId"])
        part_map[key] = part

    result = []

    # First pass: count occurrences by name to determine if enumeration is needed
    name_counts: dict[str, int] = {}
    for occ in occurrences:
        path = occ.get("path", [])
        if not path:
            continue

        final_instance_id = path[-1]
        instance = instance_map.get(final_instance_id, {})

        part_doc_id = instance.get("documentId", doc.document_id)
        part_element_id = instance.get("elementId", "")
        part_id = instance.get("partId", "")

        if not part_element_id or not part_id:
            if instance.get("type") == "Assembly":
                continue
            continue

        part_key = (part_doc_id, part_element_id, part_id)
        part_info = part_map.get(part_key, {})
        part_name = instance.get("name", part_info.get("name", f"part_{final_instance_id}"))

        name_counts[part_name] = name_counts.get(part_name, 0) + 1

    # Second pass: assign enumeration numbers and create PartOccurrence objects
    name_counters: dict[str, int] = {}

    for occ in occurrences:
        path = occ.get("path", [])
        transform_list = occ.get("transform", [])

        if not path:
            logger.warning("Occurrence without path, skipping")
            continue

        # Get the final instance ID in the path
        final_instance_id = path[-1]
        instance = instance_map.get(final_instance_id, {})

        if not instance:
            # Try to find in the occurrence itself
            logger.debug("Instance %s not found in map, using occurrence data", final_instance_id)

        # Parse the transform
        if len(transform_list) == 16:
            # Row-major 4x4 matrix
            transform = np.array(transform_list).reshape(4, 4)
        else:
            logger.warning("Invalid transform length %d for occurrence", len(transform_list))
            transform = np.eye(4)

        # Get part info - need to find which part this instance refers to
        # The instance should have documentId, elementId, partId
        part_doc_id = instance.get("documentId", doc.document_id)
        part_element_id = instance.get("elementId", "")
        part_id = instance.get("partId", "")

        if not part_element_id or not part_id:
            if instance.get("type") == "Assembly":
                continue
            logger.warning("Occurrence missing elementId or partId: %s", path)
            continue

        # Get part name
        part_key = (part_doc_id, part_element_id, part_id)
        part_info = part_map.get(part_key, {})
        part_name = instance.get("name", part_info.get("name", f"part_{final_instance_id}"))

        # Assign enumeration if there are multiple occurrences with the same name
        enumeration: int | None = None
        if name_counts.get(part_name, 0) > 1:
            name_counters[part_name] = name_counters.get(part_name, 0) + 1
            enumeration = name_counters[part_name]

        # Get configuration
        configuration = instance.get("configuration", "")

        # Try to fetch color, mass, and inertia from Onshape if client is provided
        color: tuple[int, int, int, int] | None = None
        mass: float | None = None
        center_of_mass: tuple[float, float, float] | None = None
        inertia: list[float] | None = None

        if client is not None:
            logger.debug("Fetching color for part %s", part_name)
            try:
                metadata = client.get_part_metadata(
                    document_id=part_doc_id,
                    workspace_type=doc.workspace_type,
                    workspace_id=doc.workspace_id,
                    element_id=part_element_id,
                    part_id=part_id,
                    configuration=configuration,
                )
                # Extract color from metadata
                properties = metadata.get("properties", [])
                appearance_prop = None
                for prop in properties:
                    if prop.get("name") == "Appearance":
                        appearance_prop = prop
                        break

                if appearance_prop:
                    appearance_value = appearance_prop.get("value", {})
                    color_data = appearance_value.get("color", {})
                    opacity = appearance_value.get("opacity", 255)
                    if color_data:
                        red = int(color_data.get("red", 128))
                        green = int(color_data.get("green", 128))
                        blue = int(color_data.get("blue", 128))
                        color = (red, green, blue, opacity)
                        logger.debug(
                            "Found color for part %s: RGB(%d, %d, %d) opacity=%d",
                            part_name,
                            red,
                            green,
                            blue,
                            opacity,
                        )
            except Exception as e:
                logger.warning("Could not fetch color for part %s: %s", part_name, e)

            # Fetch mass properties for mass, inertia, and center of mass
            try:
                mass_props = client.get_part_mass_properties(
                    document_id=part_doc_id,
                    workspace_type=doc.workspace_type,
                    workspace_id=doc.workspace_id,
                    element_id=part_element_id,
                    part_id=part_id,
                    configuration=configuration,
                )

                # Extract mass properties from the body
                bodies = mass_props.get("bodies", {})
                body = bodies.get(part_id, {})
                if not body and bodies:
                    # If part_id not found, try first body
                    body = list(bodies.values())[0] if bodies else {}

                if body:
                    # Extract mass (first element of mass array)
                    mass_list = body.get("mass", [])
                    if mass_list and len(mass_list) > 0:
                        mass_value = float(mass_list[0])
                        if mass_value > 0:
                            mass = mass_value
                            logger.debug("Found mass for part %s: %.6f kg", part_name, mass)
                        else:
                            logger.warning(
                                "Part %s has zero or negative mass (%.6f kg). "
                                "Setting to massless (0.0 kg) - assign a material in Onshape.",
                                part_name,
                                mass_value,
                            )
                    else:
                        has_mass = body.get("hasMass", False)
                        if not has_mass:
                            logger.warning(
                                "Part %s has no mass assigned (hasMass=false). "
                                "Setting to massless (0.0 kg) - assign a material in Onshape for accurate physics.",
                                part_name,
                            )

                    # Extract center of mass
                    centroid = body.get("centroid", [])
                    if centroid and len(centroid) >= 3:
                        center_of_mass = (float(centroid[0]), float(centroid[1]), float(centroid[2]))
                        logger.debug(
                            "Found center of mass for part %s: (%.6f, %.6f, %.6f) m",
                            part_name,
                            center_of_mass[0],
                            center_of_mass[1],
                            center_of_mass[2],
                        )

                    # Extract inertia matrix (9 elements for 3x3 matrix)
                    inertia_list = body.get("inertia", [])
                    if inertia_list and len(inertia_list) >= 9:
                        inertia = [float(x) for x in inertia_list[:9]]
                        logger.debug("Found inertia matrix for part %s", part_name)
                    elif inertia_list:
                        logger.warning(
                            "Part %s has incomplete inertia data (%d elements, expected 9). "
                            "Using minimal inertia values.",
                            part_name,
                            len(inertia_list),
                        )
                else:
                    logger.warning(
                        "No mass properties found for part %s. "
                        "Setting to massless (0.0 kg) - physics simulation may be inaccurate.",
                        part_name,
                    )
            except Exception as e:
                logger.warning(
                    "Could not fetch mass properties for part %s: %s. "
                    "Setting to massless (0.0 kg) - physics simulation may be inaccurate.",
                    part_name,
                    e,
                )

        result.append(
            PartOccurrence(
                path=path,
                transform=transform,
                document_id=part_doc_id,
                element_id=part_element_id,
                part_id=part_id,
                workspace_type=doc.workspace_type,
                workspace_id=doc.workspace_id,
                name=part_name,
                configuration=configuration,
                color=color,
                mass=mass,
                center_of_mass=center_of_mass,
                inertia=inertia,
                enumeration=enumeration,
            )
        )

    logger.info("Parsed %d part occurrences", len(result))
    return result


def generate_urdf(
    output_name: str,
    parts: list[PartOccurrence],
    mesh_dir: str = "meshes",
) -> ET.Element:
    """Generate a URDF with star topology (all parts fixed to base_link).

    Args:
        output_name: Name for the output file
        parts: List of part occurrences with their transforms
        mesh_dir: Relative path to mesh directory

    Returns:
        ElementTree root element for the URDF
    """
    robot = ET.Element("robot", name=output_name)

    # Create base_link (empty link at origin)
    base_link = ET.SubElement(robot, "link", name="base_link")

    base_inertial = ET.SubElement(base_link, "inertial")
    ET.SubElement(base_inertial, "mass", value="0.001")
    ET.SubElement(base_inertial, "origin", xyz="0 0 0", rpy="0 0 0")
    ET.SubElement(
        base_inertial,
        "inertia",
        ixx="0.000001",
        ixy="0",
        ixz="0",
        iyy="0.000001",
        iyz="0",
        izz="0.000001",
    )

    for part in parts:
        # Create link for this part
        link = ET.SubElement(robot, "link", name=part.link_name)

        # Add visual geometry
        visual = ET.SubElement(link, "visual")
        ET.SubElement(visual, "origin", xyz="0 0 0", rpy="0 0 0")
        geometry = ET.SubElement(visual, "geometry")
        mesh_path = f"{mesh_dir}/{part.mesh_filename}"
        ET.SubElement(geometry, "mesh", filename=mesh_path)

        # Add material/color if available
        if part.color is not None:
            material = ET.SubElement(visual, "material", name=f"{part.link_name}_material")
            color_elem = ET.SubElement(material, "color")
            # URDF uses RGBA in 0-1 range
            color_elem.set(
                "rgba",
                f"{part.color[0] / 255.0:.3f} {part.color[1] / 255.0:.3f} "
                f"{part.color[2] / 255.0:.3f} {part.color[3] / 255.0:.3f}",
            )

        # Add collision geometry (same as visual)
        collision = ET.SubElement(link, "collision")
        ET.SubElement(collision, "origin", xyz="0 0 0", rpy="0 0 0")
        col_geometry = ET.SubElement(collision, "geometry")
        ET.SubElement(col_geometry, "mesh", filename=mesh_path)

        # Add inertial properties (use actual values if available, otherwise massless with warning)
        inertial = ET.SubElement(link, "inertial")

        # Use actual mass if available, otherwise set to 0.0 (massless)
        if part.mass is not None and part.mass > 0:
            mass_value = part.mass
        else:
            mass_value = 0.0

        ET.SubElement(inertial, "mass", value=f"{mass_value:.6f}")

        # Set center of mass origin (use actual CoM if available, otherwise origin)
        if part.center_of_mass is not None:
            com_xyz = f"{part.center_of_mass[0]:.6f} {part.center_of_mass[1]:.6f} {part.center_of_mass[2]:.6f}"
        else:
            com_xyz = "0 0 0"
            if mass_value > 0:
                logger.warning(
                    "Part %s has mass but no center of mass data. Using origin (0, 0, 0).",
                    part.name,
                )
        ET.SubElement(inertial, "origin", xyz=com_xyz, rpy="0 0 0")

        # Set inertia matrix (use actual values if available, otherwise minimal values)
        if part.inertia is not None and len(part.inertia) >= 9:
            # Inertia matrix is stored as [Ixx, Ixy, Ixz, Iyx, Iyy, Iyz, Izx, Izy, Izz]
            # URDF expects: ixx, ixy, ixz, iyy, iyz, izz (symmetric matrix)
            ixx = part.inertia[0]
            ixy = part.inertia[1]
            ixz = part.inertia[2]
            iyy = part.inertia[4]  # Skip Iyx (same as Ixy)
            iyz = part.inertia[5]
            izz = part.inertia[8]

            # Ensure positive definite (minimum values)
            min_inertia = 1e-6
            ixx = max(ixx, min_inertia)
            iyy = max(iyy, min_inertia)
            izz = max(izz, min_inertia)

            ET.SubElement(
                inertial,
                "inertia",
                ixx=f"{ixx:.6f}",
                ixy=f"{ixy:.6f}",
                ixz=f"{ixz:.6f}",
                iyy=f"{iyy:.6f}",
                iyz=f"{iyz:.6f}",
                izz=f"{izz:.6f}",
            )
        else:
            # Use minimal inertia values (required by simulators)
            ET.SubElement(
                inertial,
                "inertia",
                ixx="0.000001",
                ixy="0",
                ixz="0",
                iyy="0.000001",
                iyz="0",
                izz="0.000001",
            )

        # Create fixed joint from base_link to this part
        # The joint origin is the world transform of the part
        xyz, rpy = matrix_to_rpy(part.transform)

        if part.enumeration is not None:
            joint_name = sanitize_name(f"joint_{part.name}_{part.enumeration}")
        else:
            joint_name = sanitize_name(f"joint_{part.name}")
        joint = ET.SubElement(robot, "joint", name=joint_name, type="fixed")
        ET.SubElement(joint, "parent", link="base_link")
        ET.SubElement(joint, "child", link=part.link_name)
        ET.SubElement(
            joint,
            "origin",
            xyz=f"{xyz[0]:.8f} {xyz[1]:.8f} {xyz[2]:.8f}",
            rpy=f"{rpy[0]:.8f} {rpy[1]:.8f} {rpy[2]:.8f}",
        )

    return robot


def indent_xml(elem: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation to XML element tree."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = indent


def convert_urdf_to_mjcf(urdf_path: Path, mjcf_path: Path, mesh_dir: str = "meshes") -> None:
    """Convert a URDF file to MJCF format.

    This is a basic converter that handles the frozen-snapshot structure:
    - All links are bodies in MJCF
    - Fixed joints become welds
    - Visual/collision meshes are converted to MJCF geometry

    Args:
        urdf_path: Path to input URDF file
        mjcf_path: Path to output MJCF file
        mesh_dir: Relative path to mesh directory
    """
    # Parse URDF
    urdf_tree = ET.parse(urdf_path)
    urdf_root = urdf_tree.getroot()

    # Create MJCF root
    mjcf = ET.Element("mujoco", model=urdf_root.get("name", "robot"))

    # Add compiler options
    compiler = ET.SubElement(mjcf, "compiler")
    compiler.set("angle", "radian")
    compiler.set("coordinate", "local")
    compiler.set("inertiafromgeom", "true")

    # Add option
    option = ET.SubElement(mjcf, "option")
    option.set("gravity", "0 0 -9.81")
    option.set("timestep", "0.002")

    # Add asset (for meshes)
    asset = ET.SubElement(mjcf, "asset")

    # Add worldbody
    worldbody = ET.SubElement(mjcf, "worldbody")

    # Process all links from URDF
    links = urdf_root.findall("link")
    base_link = None
    other_links = []

    for link in links:
        link_name = link.get("name", "")
        if link_name == "base_link":
            base_link = link
        else:
            other_links.append(link)

    # Add base_link geometry directly to worldbody (worldbody cannot have attributes)
    if base_link is not None:
        # Process base_link visual/collision directly in worldbody
        _add_link_geometry_to_body(base_link, worldbody, asset, mesh_dir, urdf_path.parent)

    # Add all other links as bodies, connected via welds (fixed joints)
    for link in other_links:
        link_name = link.get("name", "")
        body = ET.SubElement(worldbody, "body", name=link_name)

        # Find the joint that connects this link to base_link
        joint = None
        for j in urdf_root.findall("joint"):
            child_elem = j.find("child")
            if child_elem is not None and child_elem.get("link") == link_name:
                joint = j
                break

        # Set body pose from joint origin
        if joint is not None:
            origin = joint.find("origin")
            if origin is not None:
                xyz = origin.get("xyz", "0 0 0").split()
                rpy = origin.get("rpy", "0 0 0").split()
                body.set("pos", " ".join(xyz))
                # Convert RPY to quaternion for MJCF (simplified - using euler for now)
                # MJCF uses quaternions, but we can use euler attribute
                body.set("euler", " ".join(rpy))

        # Add geometry from link
        _add_link_geometry_to_body(link, body, asset, mesh_dir, urdf_path.parent)

    # Pretty print and save
    indent_xml(mjcf)
    mjcf_tree = ET.ElementTree(mjcf)
    mjcf_tree.write(mjcf_path, encoding="unicode", xml_declaration=True)


def _add_link_geometry_to_body(
    link: ET.Element, body: ET.Element, asset: ET.Element, mesh_dir: str, base_path: Path
) -> None:
    """Add visual and collision geometry from a URDF link to an MJCF body.

    Args:
        link: URDF link element
        body: MJCF body element to add geometry to
        asset: MJCF asset element for mesh definitions
        mesh_dir: Relative path to mesh directory
        base_path: Base path for resolving mesh file paths
    """
    link_name = link.get("name", "")

    # Process visual elements
    for visual in link.findall("visual"):
        geometry = visual.find("geometry")
        if geometry is not None:
            mesh_elem = geometry.find("mesh")
            if mesh_elem is not None:
                mesh_filename = mesh_elem.get("filename", "")
                # Keep mesh path relative to MJCF file location
                # The mesh_filename is already relative to the URDF, so use it as-is

                # Add mesh to asset if not already present
                mesh_name = f"{link_name}_mesh"
                existing_mesh = asset.find(f"mesh[@name='{mesh_name}']")
                if existing_mesh is None:
                    mesh_asset = ET.SubElement(asset, "mesh")
                    mesh_asset.set("name", mesh_name)
                    # Use relative path from MJCF file
                    mesh_asset.set("file", mesh_filename)

                # Add geometry to body
                geom = ET.SubElement(body, "geom")
                geom.set("type", "mesh")
                geom.set("mesh", mesh_name)

                # Add material/color if available
                material = visual.find("material")
                if material is not None:
                    color_elem = material.find("color")
                    if color_elem is not None:
                        rgba = color_elem.get("rgba", "0.5 0.5 0.5 1.0")
                        geom.set("rgba", rgba)

    # Process collision elements (add as separate geoms with contype/conaffinity)
    for collision in link.findall("collision"):
        geometry = collision.find("geometry")
        if geometry is not None:
            mesh_elem = geometry.find("mesh")
            if mesh_elem is not None:
                mesh_filename = mesh_elem.get("filename", "")

                mesh_name = f"{link_name}_collision_mesh"
                existing_mesh = asset.find(f"mesh[@name='{mesh_name}']")
                if existing_mesh is None:
                    mesh_asset = ET.SubElement(asset, "mesh")
                    mesh_asset.set("name", mesh_name)
                    # Use relative path from MJCF file
                    mesh_asset.set("file", mesh_filename)

                geom = ET.SubElement(body, "geom")
                geom.set("type", "mesh")
                geom.set("mesh", mesh_name)
                geom.set("contype", "1")
                geom.set("conaffinity", "1")
                geom.set("rgba", "0.5 0.5 0.5 0.0")  # Invisible collision

    # Add inertial properties if available (skip for worldbody)
    # Note: In MJCF, mass and inertia must be in an <inertial> child element
    # Worldbody cannot have inertial properties
    if body.tag != "worldbody":
        inertial = link.find("inertial")
        if inertial is not None:
            mass_elem = inertial.find("mass")
            inertia_elem = inertial.find("inertia")
            origin = inertial.find("origin")

            # Only create inertial element if we have mass or inertia data
            if mass_elem is not None or inertia_elem is not None:
                inertial_mjcf = ET.SubElement(body, "inertial")

                if mass_elem is not None:
                    mass_value = mass_elem.get("value", "0")
                    inertial_mjcf.set("mass", mass_value)

                # Center of mass position
                if origin is not None:
                    xyz = origin.get("xyz", "0 0 0")
                    inertial_mjcf.set("pos", xyz)

                if inertia_elem is not None:
                    # MJCF uses diaginertia (diagonal elements only)
                    ixx = inertia_elem.get("ixx", "0")
                    iyy = inertia_elem.get("iyy", "0")
                    izz = inertia_elem.get("izz", "0")
                    inertial_mjcf.set("diaginertia", f"{ixx} {iyy} {izz}")


def download_meshes(
    client: OnshapeClient,
    parts: list[PartOccurrence],
    output_dir: Path,
    units: str = "meter",
) -> None:
    """Download STL meshes for all parts.

    The STL is downloaded in the part's local frame. The world transform
    is applied via the URDF joint origin.

    Args:
        client: Onshape API client
        parts: List of part occurrences
        output_dir: Directory to save meshes
        units: Units for STL export
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, part in enumerate(parts):
        mesh_path = output_dir / part.mesh_filename

        logger.info(
            "Downloading mesh %d/%d: %s -> %s",
            i + 1,
            len(parts),
            part.name,
            mesh_path.name,
        )

        try:
            stl_data = client.download_stl(
                document_id=part.document_id,
                workspace_type=part.workspace_type,
                workspace_id=part.workspace_id,
                element_id=part.element_id,
                part_id=part.part_id,
                units=units,
            )

            with open(mesh_path, "wb") as f:
                f.write(stl_data)

            logger.debug("Saved %d bytes to %s", len(stl_data), mesh_path)

        except Exception as e:
            logger.error("Failed to download mesh for %s: %s", part.name, e)
            raise


def run_export(target_dir: str | Path) -> Path:
    """Run the full export pipeline.

    Args:
        target_dir: Directory containing config.json

    Returns:
        Path to the generated URDF file
    """
    target_dir = Path(target_dir)
    config_path = target_dir / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load configuration
    config = ExportConfig.from_json(config_path)
    logger.info("Loaded config from %s", config_path)
    logger.info("Document URL: %s", config.url)

    # Initialize client
    client = OnshapeClient()

    # Parse document URL
    doc = client.parse_url(config.url)
    logger.info(
        "Document: %s / %s / %s / %s",
        doc.document_id,
        doc.workspace_type,
        doc.workspace_id,
        doc.element_id,
    )

    # Fetch assembly definition (includes occurrences with global transforms)
    logger.info("Fetching assembly definition...")
    assembly = client.get_assembly(doc)

    # Extract occurrences from the assembly response
    # Occurrences are in rootAssembly.occurrences and contain the global transforms
    root_assembly = assembly.get("rootAssembly", {})
    raw_occurrences = root_assembly.get("occurrences", [])
    logger.info("Found %d occurrences in assembly", len(raw_occurrences))

    # Parse occurrences
    logger.info("Parsing occurrences...")
    parts = parse_occurrences(raw_occurrences, cast(AssemblyDict, assembly), doc, client=client)

    if not parts:
        raise ValueError("No parts found in assembly. Check that the assembly is not empty.")

    logger.info("Found %d parts to export", len(parts))

    # Download meshes
    mesh_dir = config.output_dir / config.mesh_dir
    logger.info("Downloading meshes to %s...", mesh_dir)
    download_meshes(client, parts, mesh_dir, units=config.units)

    # Generate URDF (always generate URDF first, then convert if needed)
    logger.info("Generating URDF...")
    urdf_root = generate_urdf(config.output_name, parts, mesh_dir=config.mesh_dir)

    # Pretty print and save URDF
    indent_xml(urdf_root)
    urdf_path = config.output_dir / f"{config.output_name}.urdf"

    tree = ET.ElementTree(urdf_root)
    tree.write(urdf_path, encoding="unicode", xml_declaration=True)

    logger.info("URDF saved to %s", urdf_path)

    # Convert to MJCF if requested
    output_path = urdf_path
    if config.filetype == "mjcf":
        logger.info("Converting URDF to MJCF...")
        mjcf_path = config.output_dir / f"{config.output_name}.mjcf"
        convert_urdf_to_mjcf(urdf_path, mjcf_path, mesh_dir=config.mesh_dir)
        logger.info("MJCF saved to %s", mjcf_path)
        output_path = mjcf_path

    # Summary
    logger.info("=" * 60)
    logger.info("Export complete!")
    logger.info("  Output: %s", output_path)
    if config.filetype == "mjcf":
        logger.info("  URDF: %s (intermediate)", urdf_path)
    logger.info("  Meshes: %s (%d files)", mesh_dir, len(parts))
    logger.info("  Parts: %d", len(parts))
    logger.info("=" * 60)

    return output_path
