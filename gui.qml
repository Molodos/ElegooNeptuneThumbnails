// Copyright (c) 2023 Molodos
// The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import QtQuick.Window 2.2
import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3

import UM 1.5 as UM
import Cura 1.1 as Cura


// Settings popup window
Window
{
    id: popupWindow
    minimumWidth: Math.round(UM.Theme.getSize("modal_window_minimum").width)
    minimumHeight: Math.round(UM.Theme.getSize("modal_window_minimum").height)
    maximumWidth: Math.round(minimumWidth * 1.2)
    maximumHeight: Math.round(minimumHeight * 1.2)
    modality: Qt.ApplicationModal
    width: minimumWidth
    height: minimumHeight
    color: UM.Theme.getColor("main_background")
    title: "Elegoo Neptune Thumbnails"

    // Check if the window is closed
    onVisibleChanged:
    {
        if (!visible)
        {
            plugin.popup_closed()
        }
    }

    // Add margin around window contents
    Item
    {
        anchors.fill: parent
        anchors.margins: UM.Theme.getSize("wide_margin").width

        // Title
        UM.Label
        {
            id: title
            anchors.top: parent.top
            text: "Thumbnails Settings"
            font: UM.Theme.getFont("large")
            Layout.fillWidth: true
        }


        // Row 2: Setting items
        ColumnLayout
        {
            spacing: Math.round(UM.Theme.getSize("wide_margin").height / 2)
            anchors.top: title.bottom
            anchors.topMargin: UM.Theme.getSize("wide_margin").width

            // Settings item: Enable checkbox
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width
                height: 50 * screenScaleFactor

                // Checkbox
                UM.CheckBox
                {
                    id: thumbnailsEnabled
                    checked: settings.are_thumbnails_enabled
                    onClicked: settings.set_thumbnails_enabled(thumbnailsEnabled.checked)
                    text: "Enable Thumbnails"
                    tooltip: "Thumbnails will be added when saving a G-code file"
                }
            }

            // Settings item: Top left corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width
                height: 50 * screenScaleFactor

                // Name
                UM.Label
                {
                    text: "Top Left Corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 100 * screenScaleFactor
                    Layout.maximumWidth: 500 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                Cura.SecondaryButton
                {
                    text: "Select"
                    enabled: True
                }
            }

            // Settings item: Top right corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width
                height: 50 * screenScaleFactor

                // Name
                UM.Label
                {
                    text: "Top Right Corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 100 * screenScaleFactor
                    Layout.maximumWidth: 500 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                Cura.SecondaryButton
                {
                    text: "Select"
                    enabled: True
                }
            }

            // Settings item: Bottom left corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width
                height: 50 * screenScaleFactor

                // Name
                UM.Label
                {
                    text: "Bottom Left Corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 100 * screenScaleFactor
                    Layout.maximumWidth: 500 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                Cura.SecondaryButton
                {
                    text: "Select"
                    enabled: True
                }
            }

            // Settings item: Bottom right corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width
                height: 50 * screenScaleFactor

                // Name
                UM.Label
                {
                    text: "Bottom Right Corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 100 * screenScaleFactor
                    Layout.maximumWidth: 500 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                Cura.SecondaryButton
                {
                    text: "Select"
                    enabled: True
                }
            }
        }

        // Save elements
        RowLayout
        {
            anchors.bottom: parent.bottom
            anchors.right: parent.right

            Cura.TertiaryButton
            {
                text: "Cancel"
                onClicked: popupWindow.close()
            }

            // Save button
            Cura.PrimaryButton
            {
                text: "Save"
                iconSource: UM.Theme.getIcon("Save")
                onClicked: plugin.save_clicked()
            }
        }
    }
}
