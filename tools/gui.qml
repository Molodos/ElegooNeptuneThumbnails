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
    minimumHeight: Math.round(UM.Theme.getSize("modal_window_minimum").height / 6 * 5)
    maximumWidth: minimumWidth
    maximumHeight: minimumHeight
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
            settings.restore()
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
            text: "Thumbnail Settings"
            font: UM.Theme.getFont("large")
            Layout.fillWidth: true
        }

        // Setting items
        ColumnLayout
        {
            id: settingCol
            anchors.top: title.bottom
            anchors.topMargin: Math.round(UM.Theme.getSize("wide_margin").width / 2)
            spacing: Math.round(UM.Theme.getSize("wide_margin").width / 2)

            // Settings item: Enable checkbox
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Checkbox
                UM.CheckBox
                {
                    id: thumbnailsEnabled
                    checked: settings.thumbnails_enabled
                    onClicked: settings.set_thumbnails_enabled(thumbnailsEnabled.checked)
                    text: "Enable thumbnails"
                    tooltip: "Thumbnails will be added when saving a G-code file"
                }
            }

            // Settings item: Printer model
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Name
                UM.Label
                {
                    text: "Printer model"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 150 * screenScaleFactor
                    Layout.maximumWidth: 150 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                ComboBox {
                    Layout.minimumWidth: 200 * screenScaleFactor
                    Layout.maximumWidth: 200 * screenScaleFactor
                    currentIndex: settings.selected_printer_model
                    model: settings.printer_model_list
                    onCurrentIndexChanged: settings.select_printer_model(currentIndex)
                }
            }

            // Settings item: Top left corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Name
                UM.Label
                {
                    text: "Top left corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 150 * screenScaleFactor
                    Layout.maximumWidth: 150 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                ComboBox {
                    Layout.minimumWidth: 200 * screenScaleFactor
                    Layout.maximumWidth: 200 * screenScaleFactor
                    currentIndex: [settings.select_corner(0), settings.selected_corner_option][1]
                    model: settings.option_list
                    onCurrentIndexChanged: settings.set_corner_option(0, currentIndex)
                }
            }

            // Settings item: Top right corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Name
                UM.Label
                {
                    text: "Top right corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 150 * screenScaleFactor
                    Layout.maximumWidth: 150 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                ComboBox {
                    Layout.minimumWidth: 200 * screenScaleFactor
                    Layout.maximumWidth: 200 * screenScaleFactor
                    currentIndex: [settings.select_corner(1), settings.selected_corner_option][1]
                    model: settings.option_list
                    onCurrentIndexChanged: settings.set_corner_option(1, currentIndex)
                }
            }

            // Settings item: Bottom left corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Name
                UM.Label
                {
                    text: "Bottom left corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 150 * screenScaleFactor
                    Layout.maximumWidth: 150 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                ComboBox {
                    Layout.minimumWidth: 200 * screenScaleFactor
                    Layout.maximumWidth: 200 * screenScaleFactor
                    currentIndex: [settings.select_corner(2), settings.selected_corner_option][1]
                    model: settings.option_list
                    onCurrentIndexChanged: settings.set_corner_option(2, currentIndex)
                }
            }

            // Settings item: Bottom right corner
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Name
                UM.Label
                {
                    text: "Bottom right corner"
                    elide: Text.ElideRight
                    Layout.minimumWidth: 150 * screenScaleFactor
                    Layout.maximumWidth: 150 * screenScaleFactor
                    Layout.fillWidth: true
                }

                // Setting
                ComboBox {
                    Layout.minimumWidth: 200 * screenScaleFactor
                    Layout.maximumWidth: 200 * screenScaleFactor
                    currentIndex: [settings.select_corner(3), settings.selected_corner_option][1]
                    model: settings.option_list
                    onCurrentIndexChanged: settings.set_corner_option(3, currentIndex)
                }
            }

            // Settings item: Enable statistics
            RowLayout
            {
                spacing: UM.Theme.getSize("wide_margin").width
                width: parent.width

                // Checkbox
                UM.CheckBox
                {
                    id: statisticsEnabled
                    checked: settings.statistics_enabled
                    onClicked: settings.set_statistics_enabled(statisticsEnabled.checked)
                    text: "Send anonymous usage statistics"
                    tooltip: "Statistics will help to improve the plugin in the future"
                }
            }
        }

        // Thumbnail title
        UM.Label
        {
            anchors.top: title.top
            anchors.left: thumbnail.left
            text: "Preview"
            font: UM.Theme.getFont("large")
            Layout.fillWidth: true
        }

        // Thumbnail header
        UM.Label
        {
            id: thumbHeader
            anchors.top: settingCol.top
            anchors.left: thumbnail.left
            text: "Values are just examples for showcase"
            elide: Text.ElideRight
            Layout.minimumWidth: 250 * screenScaleFactor
            Layout.maximumWidth: 250 * screenScaleFactor
            Layout.fillWidth: true
        }

        // Thumbnail dimensions
        Item
        {
            id: thumbnail
            anchors.top: thumbHeader.bottom
            anchors.right: parent.right
            anchors.topMargin: Math.round(UM.Theme.getSize("wide_margin").width / 2)
            height: 250 * screenScaleFactor
            width: 250 * screenScaleFactor

            // Thumbnail image
            Image
            {
                anchors.fill: parent
                source: "../img/bg_thumbnail.png"
                fillMode: Image.PreserveAspectFit
            }
        }

        // Checkbox
        UM.CheckBox
        {
            anchors.top: thumbnail.bottom
            anchors.left: thumbnail.left
            anchors.topMargin: Math.round(UM.Theme.getSize("wide_margin").width / 2)
            id: useCurrentModel
            checked: settings.use_current_model
            onClicked: settings.set_use_current_model(useCurrentModel.checked)
            text: "Use current model(s)"
            tooltip: "Use the currently loaded model(s) from Cura for preview"
        }

        // Donation title
        UM.Label
        {
            anchors.bottom: donationButton.top
            anchors.left: parent.left
            anchors.bottomMargin: Math.round(UM.Theme.getSize("wide_margin").width / 2)
            text: "Like this plugin? Consider supporting me :)"
            font: UM.Theme.getFont("large")
            Layout.fillWidth: true
        }

        // Donate button
        Item
        {
            id: donationButton
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            height: 50 * screenScaleFactor
            width: 200 * screenScaleFactor

            // Donate image
            Image
            {
                anchors.fill: parent
                source: "https://img.buymeacoffee.com/button-api/?text=Buy%20me%20a%20coffee&emoji=&slug=molodos&button_colour=196EF0&font_colour=ffffff&font_family=Comic&outline_colour=000000&coffee_colour=FFDD00"
                fillMode: Image.PreserveAspectFit

                // Clickable
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: Qt.openUrlExternally("https://www.buymeacoffee.com/molodos");
                }
            }
        }

        // Save elements
        RowLayout
        {
            id: save
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
                onClicked: [settings.save(), popupWindow.close()]
            }
        }
    }
}
