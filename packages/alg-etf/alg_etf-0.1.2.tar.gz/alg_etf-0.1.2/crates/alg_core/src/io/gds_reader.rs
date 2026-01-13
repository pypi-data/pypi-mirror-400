use crate::geo::{Path as AlgPath, Polygon, Rectangle, Shape, Vertex};
use crate::{
    geo::path::EndStyle,
    library::{
        Cell, Library,
        instance::{Instance, Orientation, Translate},
        layer::LayerId,
    },
};
use gds21::{self, GdsElement, GdsLibrary, GdsStrans};
use std::path::Path;

/// The GdsReader provides functionality to read GDSII files and convert them into the internal
/// representation.
pub struct GdsReader;

impl GdsReader {
    /// Reads a GDSII file from the given path and returns a Library.
    pub fn read_file<P: AsRef<Path>>(path: P) -> Result<Library, String> {
        let gds_lib =
            GdsLibrary::load(path).map_err(|e| format!("Failed to load GDS file: {}", e))?;

        Self::convert_library(gds_lib)
    }

    /// Converts a gds21::GdsLibrary into our internal Library.
    pub fn convert_library(gds_lib: GdsLibrary) -> Result<Library, String> {
        let mut lib = Library::new(gds_lib.name.clone());

        // Pass 1: Create all cells within the library.
        // This automatically assigns unique IDs and populates the name lookup.
        for gds_struct in &gds_lib.structs {
            lib.create_cell(gds_struct.name.clone());
        }

        // Pass 2: Populate each cell with elements (Shapes & Instances)
        for gds_struct in &gds_lib.structs {
            let cell_id = lib
                .get_id_by_name(&gds_struct.name)
                .ok_or_else(|| format!("Cell {} disappeared during import", gds_struct.name))?;

            // Create a local detached cell
            let mut cell = Cell::new(gds_struct.name.clone());

            for element in &gds_struct.elems {
                match element {
                    GdsElement::GdsBoundary(b) => {
                        let layer = LayerId::from(b.layer as u8);
                        let vertices: Vec<Vertex> =
                            b.xy.iter().map(|p| Vertex::new(p.x, p.y)).collect();
                        cell.add_shape(layer, Shape::Polygon(Polygon::new(vertices)));
                    }
                    GdsElement::GdsBox(b) => {
                        let layer = LayerId::from(b.layer as u8);
                        if b.xy.len() >= 2 {
                            let min_x = b.xy.iter().map(|p| p.x).min().unwrap_or(0);
                            let min_y = b.xy.iter().map(|p| p.y).min().unwrap_or(0);
                            let max_x = b.xy.iter().map(|p| p.x).max().unwrap_or(0);
                            let max_y = b.xy.iter().map(|p| p.y).max().unwrap_or(0);

                            let rect = Rectangle::new(
                                Vertex::new(min_x, min_y),
                                Vertex::new(max_x, max_y),
                            );
                            cell.add_shape(layer, Shape::Rectangle(rect));
                        }
                    }
                    GdsElement::GdsPath(p) => {
                        let layer = LayerId::from(p.layer as u8);
                        let vertices: Vec<Vertex> =
                            p.xy.iter().map(|v| Vertex::new(v.x, v.y)).collect();
                        let width = p.width.unwrap_or(0) as u32;
                        let endstyle = match p.path_type.unwrap_or(0) {
                            0 => EndStyle::Butt,
                            1 => EndStyle::Round,
                            2 => EndStyle::Square,
                            _ => EndStyle::Butt, // Default fallback
                        };
                        cell.add_shape(layer, Shape::Path(AlgPath::new(vertices, width, endstyle)));
                    }
                    GdsElement::GdsStructRef(inst) => {
                        if let Some(target_id) = lib.get_id_by_name(&inst.name) {
                            let translation = Self::map_strans(&inst.strans, inst.xy.x, inst.xy.y);
                            let instance = Instance::new(
                                format!("{}_{}", inst.name, cell.instances().len()),
                                target_id,
                                translation,
                            );
                            // We pass the library reference to update boundaries
                            cell.add_instance(instance, &lib);
                        }
                    }
                    _ => {} // Ignore Text and other elements
                }
            }

            // Put the fully populated cell back into the library.
            // We manually set the ID back to the original one to avoid duplicates.
            cell.set_id(cell_id);
            lib.add_cell(cell);
        }

        Ok(lib)
    }

    /// Maps GDSII strans (Structure Transformation) to our Translate and Orientation.
    fn map_strans(strans: &Option<GdsStrans>, x: i32, y: i32) -> Translate {
        let mut reflected = false;
        let mut angle = 0.0;

        if let Some(s) = strans {
            reflected = s.reflected;
            angle = s.angle.unwrap_or(0.0);
        }

        // Map GDSII logic: Reflected (Mirror across X) then Rotate
        let orientation = match (reflected, angle as i32) {
            (false, 0) => Orientation::R0,
            (false, 90) => Orientation::R90,
            (false, 180) => Orientation::R180,
            (false, 270) => Orientation::R270,
            (true, 0) => Orientation::MX,
            (true, 90) => Orientation::MX90,
            (true, 180) => Orientation::MX180,
            (true, 270) => Orientation::MX270,
            _ => {
                // For non-orthogonal angles, fallback to R0 for now
                // In a real tool we might want to warn or handle it
                Orientation::R0
            }
        };

        Translate::new(Vertex::new(x, y), orientation)
    }
}
