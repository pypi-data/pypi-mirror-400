use std::collections::HashMap;

use crate::{
    geo::{Boundary, Shape},
    library::{Layer, Library, instance::Instance, layer::LayerId},
};

/// A unique identifier for a Cell definition within the library.
///
/// This acts as a handle to look up `Cell` structs.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum CellId {
    /// The cell is not yet registered in a library and has no unique ID.
    Detached,
    /// A unique numeric identifier assigned by a library.
    Id(u8),
}

impl From<u8> for CellId {
    fn from(value: u8) -> Self {
        CellId::Id(value)
    }
}

impl std::fmt::Display for CellId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Detached => write!(f, "Detached"),
            Self::Id(id) => write!(f, "ID:{}", id),
        }
    }
}

/// Represents a fundamental unit of design reuse (e.g., a Logic Gate or IP Block).
///
/// A `Cell` is the primary container in hierarchical layouts. It contains:
/// 1.  **Geometry:** Shapes distributed across different physical [`Layer`]s.
/// 2.  **Hierarchy:** [`Instance`]s of other cells (allowing for nested designs).
/// 3.  **Boundaries:** A calculated geometric footprint used for placement and DRC checks.
#[derive(Clone, Debug)]
pub struct Cell {
    /// The human-readable name of the cell (e.g., "NAND2_X1").
    name: String,
    /// The unique internal identifier.
    cell_id: CellId,
    /// A collection of geometric layers, indexed by their ID.
    layers: HashMap<LayerId, Layer>,
    /// A list of child instances placed within this cell.
    instances: Vec<Instance>,
    /// The cached geometric boundary of the entire cell (including all layers/instances and their
    /// DRC padding).
    cell_boundary: Boundary,
}

impl Cell {
    /// Creates a new, empty Cell definition.
    ///
    /// # Note
    /// It is generally preferred to use [`crate::library::Library::create_cell`]
    /// which automatically handles ID generation and library registration.
    pub fn new(name: String) -> Self {
        Self {
            name,
            cell_id: CellId::Detached,
            layers: HashMap::new(),
            instances: Vec::new(),
            cell_boundary: Boundary::new(),
        }
    }

    /// Returns the cell's name.
    pub const fn name(&self) -> &String {
        &self.name
    }

    /// Returns the unique ID of this cell.
    pub const fn cell_id(&self) -> CellId {
        self.cell_id
    }

    /// Internal method to update the CellId when adding to a library.
    pub(crate) fn set_id(&mut self, id: CellId) {
        self.cell_id = id;
    }

    /// Retrieves a reference to a specific layer, if it exists.
    pub fn get_layer(&self, layer_id: &LayerId) -> Option<&Layer> {
        self.layers.get(layer_id)
    }

    pub const fn layers(&self) -> &HashMap<LayerId, Layer> {
        &self.layers
    }

    /// Returns the list of child instances.
    pub const fn instances(&self) -> &Vec<Instance> {
        &self.instances
    }

    /// Returns the cached outer boundary of the cell.
    pub const fn cell_boundary(&self) -> &Boundary {
        &self.cell_boundary
    }

    /// Explicitly adds a pre-constructed Layer object.
    pub fn add_layer(&mut self, layer: Layer, layer_id: LayerId) {
        self.layers.insert(layer_id, layer);
    }

    /// Adds an instance of another cell into this cell.
    pub fn add_instance(&mut self, instance: Instance, library: &Library) {
        let cell_id = instance.cell_id();

        match library.get_cell(cell_id) {
            Some(master_cell) => {
                let master_boundary = master_cell.cell_boundary();
                let transformed_boundary = master_boundary.transform(instance.translation());
                self.cell_boundary.merge(&transformed_boundary);
            }
            None => {
                eprintln!("Warning: Instance refers to unknown CellId {:?}", cell_id);
            }
        }

        self.instances.push(instance);
    }

    /// Adds a primitive shape to a specific [Layer].
    pub fn add_shape<I: Into<LayerId>>(&mut self, layer_id: I, shape: Shape) {
        let id = layer_id.into();
        self.layers
            .entry(id)
            .or_insert_with(|| Layer::new(id))
            .add_shape(shape.clone());

        self.cell_boundary.from_shape(&shape);
    }
}
