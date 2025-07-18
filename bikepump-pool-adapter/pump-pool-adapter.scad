
difference() {
    union() {
        linear_extrude(height=15) {
            circle(d=4, $fn=50);
        };
        translate([0, 0, 15]) {
            cylinder(h=20, d1=12, d2=4, $fn=60);
        }
    }
    
    linear_extrude(height=35) {
        // D 2 is too small because printer, too much resistance from piece.
        circle(d=3, $fn=50);
    };
}
