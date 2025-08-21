import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import "components"

Window {
    id: root
    width: 520
    height: 280
    visible: true
    color: "transparent"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    Rectangle {
        anchors.fill: parent
        radius: 16
        color: "#1A1A1A"
        opacity: 0.9
        border.color: "#33FFFFFF"
        border.width: 1
        layer.enabled: true
        layer.effect: DropShadow {
            color: "#66000000"
            radius: 24
            samples: 32
            horizontalOffset: 0
            verticalOffset: 8
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 16

            Text { 
                text: "Nova Prime"
                color: "white"
                font.pixelSize: 22
                font.bold: true
            }
            
            Text { 
                text: novaState.status
                color: "#DDFFFFFF"
                font.pixelSize: 14
            }
            
            AuroraWave { 
                Layout.fillWidth: true
                Layout.fillHeight: true
                listening: novaState.listening
            }
        }
    }

    MouseArea { 
        anchors.fill: parent
        drag.target: root
    }
}