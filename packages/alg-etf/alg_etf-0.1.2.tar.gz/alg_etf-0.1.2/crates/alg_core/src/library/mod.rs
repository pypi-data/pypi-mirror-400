//! # Layout Database Module
//!
//! This module implements the hierarchical database for storing physical design data.
//! It mimics the structure of standard layout formats like GDSII.
//!
//! ## Core Hierarchy
//!
//! The database is organized as a tree:
//! * **[`Library`]:** The top-level container (database). It holds a collection of unique Cells.
//! * **[`Cell`]:** A reusable design block (e.g., "NAND Gate").
//!     * Contains **[`Layer`]s**: Collections of geometric shapes (Polygons, Rectangles).
//!     * Contains **[`instance::Instance`]s**: References to other Cells (hierarchy).
//!
//! ## Example Workflow
//!
//! ```rust
//! use alg_core::library::{Library, Cell, CellId, LayerId};
//! use alg_core::geo::{Shape, Rectangle, Vertex};
//!
//! // 1. Initialize the Library
//! let mut lib = Library::new("MyChipLib".to_string());
//!
//! // 2. Create a Cell (e.g., a simple Macro)
//! let mut my_cell = Cell::new("Macro_A".to_string());
//!
//! // 3. Add geometry to the Cell
//! let layer_m1 = LayerId(10);
//! let rect = Shape::Rectangle(Rectangle::new(Vertex::new(0,0), Vertex::new(100,100)));
//! my_cell.add_shape(layer_m1, rect);
//!
//! // 4. Register the Cell in the Library
//! lib.add_cell(my_cell);
//! ```
pub mod cell;
pub mod instance;
pub mod layer;

use std::collections::HashMap;

pub use cell::{Cell, CellId};
pub use instance::{Instance, Orientation, Translate};
pub use layer::{Layer, LayerId};

use std::sync::atomic::{AtomicUsize, Ordering};

/// Represents a complete Design Library (database).
///
/// The `Library` is the top-level container for all [`Cell`] definitions in a layout.
/// It acts as the central registry, ensuring that every cell has a unique ID and a unique Name.
#[derive(Debug)]
pub struct Library {
    /// The name of the library.
    name: String,
    /// Primary storage: Maps numeric IDs to Cell definitions.
    cells: HashMap<CellId, Cell>,
    /// Lookup Index: Maps human-readable names to numeric IDs.
    name_to_id: HashMap<String, CellId>,
    /// Counter for automatic ID generation, using an atomic for thread-safety.
    next_id: AtomicUsize,
}

// Custom Clone implementation since AtomicUsize doesn't implement Clone
impl Clone for Library {
    fn clone(&self) -> Self {
        Self {
            name: self.name.clone(),
            cells: self.cells.clone(),
            name_to_id: self.name_to_id.clone(),
            next_id: AtomicUsize::new(self.next_id.load(Ordering::SeqCst)),
        }
    }
}

impl Library {
    /// Creates a new, empty Library.
    pub fn new(name: String) -> Self {
        Self {
            name,
            cells: HashMap::new(),
            name_to_id: HashMap::new(),
            next_id: AtomicUsize::new(0),
        }
    }

    /// Generates a new unique CellId.
    ///
    /// This method is thread-safe and can be called from multiple threads
    /// to reserve IDs before cells are even created.
    pub fn generate_id(&self) -> CellId {
        let id = self.next_id.fetch_add(1, Ordering::SeqCst);
        if id > 255 {
            panic!("Cell library overflow: exceeded 255 cells");
        }
        CellId::Id(id as u8)
    }

    /// Creates a new cell within the library with an automatically generated ID.
    pub fn create_cell(&mut self, name: String) -> CellId {
        let id = self.generate_id();
        let cell = Cell::new(name.clone());
        self.name_to_id.insert(name, id);
        self.cells.insert(id, cell);
        id
    }

    /// Adds a pre-existing Cell definition to the library.
    ///
    /// If the cell is 'Detached', it will be assigned a new ID.
    /// If it has an ID, the library's counter will be synchronized to avoid collisions.
    pub fn add_cell(&mut self, mut cell: Cell) -> CellId {
        let id = match cell.cell_id() {
            CellId::Detached => {
                let new_id = self.generate_id();
                cell.set_id(new_id);
                new_id
            }
            CellId::Id(val) => {
                // Synchronize the counter: ensure next_id is > any manually added ID.
                let mut current = self.next_id.load(Ordering::SeqCst);
                while (val as usize) >= current {
                    match self.next_id.compare_exchange(
                        current,
                        (val as usize) + 1,
                        Ordering::SeqCst,
                        Ordering::SeqCst,
                    ) {
                        Ok(_) => break,
                        Err(actual) => current = actual,
                    }
                }
                CellId::Id(val)
            }
        };

        self.name_to_id.insert(cell.name().clone(), id);
        self.cells.insert(id, cell);
        id
    }

    /// Returns the name of the library.
    pub const fn name(&self) -> &String {
        &self.name
    }

    /// Returns the complete map of all cells in the library.
    pub const fn cells(&self) -> &HashMap<CellId, Cell> {
        &self.cells
    }

    /// Retrieves a reference to a Cell using its unique ID.
    pub fn get_cell(&self, id: CellId) -> Option<&Cell> {
        self.cells.get(&id)
    }

    /// Retrieves a mutable reference to a Cell using its unique ID.
    pub fn get_cell_mut(&mut self, id: CellId) -> Option<&mut Cell> {
        self.cells.get_mut(&id)
    }

    /// Retrieves a reference to a Cell using its name.
    pub fn get_cell_by_name(&self, name: &str) -> Option<&Cell> {
        self.name_to_id.get(name).and_then(|id| self.cells.get(id))
    }

    /// Returns the ID of a cell by its name.
    pub fn get_id_by_name(&self, name: &str) -> Option<CellId> {
        self.name_to_id.get(name).copied()
    }
}
