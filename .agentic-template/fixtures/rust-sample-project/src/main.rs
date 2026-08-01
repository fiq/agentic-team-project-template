//! Orbit — a tiny 2D orbital physics sandbox.
//!
//! A single planet and a ship. The ship has a velocity; gravity bends its
//! path. Press space to thrust, R to reset. The game is intentionally simple:
//! one file, no dependencies, deterministic physics.

use std::io::{self, Write};

/// Gravitational constant for the toy universe.
const G: f64 = 0.5;
/// Planet mass.
const PLANET_MASS: f64 = 1000.0;
/// Planet position (centre of the screen).
const PLANET: (f64, f64) = (40.0, 20.0);
/// Ship thrust magnitude per frame.
const THRUST: f64 = 0.02;

#[derive(Clone, Copy)]
struct Body {
    x: f64,
    y: f64,
    vx: f64,
    vy: f64,
}

impl Body {
    fn new(x: f64, y: f64, vx: f64, vy: f64) -> Self {
        Self { x, y, vx, vy }
    }

    /// Apply Newtonian gravity toward the planet and integrate one step.
    fn step(&mut self) {
        let dx = PLANET.0 - self.x;
        let dy = PLANET.1 - self.y;
        let dist_sq = dx * dx + dy * dy;
        let dist = dist_sq.sqrt().max(1e-6);
        let accel = G * PLANET_MASS / dist_sq;
        self.vx += accel * dx / dist;
        self.vy += accel * dy / dist;
        self.x += self.vx;
        self.y += self.vy;
    }
}

fn render(ship: &Body) -> String {
    let mut grid = vec![vec![' '; 80]; 40];
    // Planet.
    let (px, py) = PLANET;
    grid[py as usize][px as usize] = '@';
    // Ship.
    let sx = ship.x.round() as usize;
    let sy = ship.y.round() as usize;
    if sy < 40 && sx < 80 {
        grid[sy][sx] = 'o';
    }
    grid.iter()
        .map(|row| row.iter().collect::<String>())
        .collect::<Vec<_>>()
        .join("\n")
}

fn main() {
    let mut ship = Body::new(10.0, 10.0, 0.4, 0.0);
    println!("Orbit — space to thrust, r to reset, q to quit.");
    loop {
        print!("\x1b[2J\x1b[H{}", render(&ship));
        io::stdout().flush().unwrap();
        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        match input.trim() {
            "q" => break,
            "r" => ship = Body::new(10.0, 10.0, 0.4, 0.0),
            " " => {
                ship.vx += THRUST;
                ship.vy -= THRUST;
            }
            _ => {}
        }
        ship.step();
    }
}
