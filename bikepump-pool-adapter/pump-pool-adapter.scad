
difference() {
    union() {
        linear_extrude(height=15) {
            circle(d=3.7, $fn=50);
        };
        translate([0, 0, 15]) {
            cylinder(h=20, d1=12, d2=4, $fn=60);
        }
    }
    
    linear_extrude(height=35) {
        circle(d=2, $fn=50);
    };
}
