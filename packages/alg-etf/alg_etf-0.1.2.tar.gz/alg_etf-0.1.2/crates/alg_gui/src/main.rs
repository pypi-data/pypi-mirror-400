use alg_core::io::gds_reader::GdsReader;
use alg_core::library::layer::LayerId;
use alg_core::project::{Design, FillStyle, LayerStyle, Technology};
use alg_gui::viewer::LayoutViewer;
use eframe::egui::Color32;

fn main() -> eframe::Result<()> {
    // 1. Setup Technology with some basic default layers
    // (In a real app, this would be loaded from a tech file)
    let mut tech = Technology::new();

    // Add some common GDS layers colors if we know them,
    // otherwise the viewer will create random ones.
    for i in 0..100 {
        let lid = LayerId::from(i as u8);
        tech.add_layer_def(
            lid,
            format!("Layer_{}", i),
            LayerStyle {
                color: Color32::from_rgb(
                    ((i * 50) % 255) as u8,
                    ((i * 80) % 255) as u8,
                    ((i * 120) % 255) as u8,
                ),
                visible: true,
                fill: FillStyle::Solid,
                name: format!("Layer_{}", i),
            },
        );
    }

    // 2. Load the GDS file
    let gds_path = "/Users/timvandenakker/Downloads/inv.gds2";
    println!("Loading GDS: {}", gds_path);

    let lib = match GdsReader::read_file(gds_path) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("Error loading GDS: {}", e);
            return Ok(());
        }
    };

    println!(
        "Loaded library: {} with {} cells",
        lib.name(),
        lib.cells().len()
    );

    // 3. Create Design
    let design = Design::new(tech, lib);

    // 4. Launch Viewer
    let options = eframe::NativeOptions {
        viewport: eframe::egui::ViewportBuilder::default().with_inner_size([1200.0, 800.0]),
        ..Default::default()
    };

    eframe::run_native(
        &format!("GDS Viewer - {}", gds_path),
        options,
        Box::new(|_cc| Ok(Box::new(LayoutViewer::new(design)))),
    )
}
