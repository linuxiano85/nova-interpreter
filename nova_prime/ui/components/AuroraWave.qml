import QtQuick 2.15
import QtQuick.Shapes 1.15

Item {
    id: root
    property bool listening: true
    property real amp: listening ? 60 : 10

    Rectangle {
        anchors.fill: parent
        radius: 12
        opacity: 0.45
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#40FF7EB6" }
            GradientStop { position: 0.5; color: "#4047C1FF" }
            GradientStop { position: 1.0; color: "#40A3FF7E" }
        }
    }

    Shape {
        anchors.fill: parent
        opacity: 0.9
        ShapePath {
            strokeWidth: 0
            fillGradient: LinearGradient {
                x1: 0; y1: 0; x2: root.width; y2: root.height
                GradientStop { position: 0.0; color: "#99FFFFFF" }
                GradientStop { position: 1.0; color: "#33FFFFFF" }
            }
            Path {
                startX: 0; startY: root.height*0.6
                PathCubic { 
                    x: root.width*0.33; y: root.height*0.4
                    control1X: root.width*0.16; control1Y: root.height*(0.6 - amp/200)
                    control2X: root.width*0.16; control2Y: root.height*(0.4 + amp/200)
                }
                PathCubic { 
                    x: root.width*0.66; y: root.height*0.7
                    control1X: root.width*0.5; control1Y: root.height*(0.4 - amp/200)
                    control2X: root.width*0.5; control2Y: root.height*(0.7 + amp/200)
                }
                PathCubic { 
                    x: root.width; y: root.height*0.5
                    control1X: root.width*0.83; control1Y: root.height*(0.7 - amp/200)
                    control2X: root.width*0.83; control2Y: root.height*(0.5 + amp/200)
                }
                PathLine { x: root.width; y: root.height }
                PathLine { x: 0; y: root.height }
                PathLine { x: 0; y: root.height*0.6 }
            }
        }
    }

    NumberAnimation on amp { 
        from: 30; to: 80
        duration: 1600
        loops: Animation.Infinite
        easing.type: Easing.InOutSine
        running: listening
    }
}