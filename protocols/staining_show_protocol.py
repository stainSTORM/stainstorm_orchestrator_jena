import json
from opentrons import protocol_api, types

metadata = {
    "protocolName": "staining_show_protocol",
    "author": "Stephan Becker openUC2",
    "description": "a show protocol which visualize the stainstorm staining process",
    "created": "2026-09-28T11:08:24.850Z",
    "internalAppBuildDate": "Thu, 13 Aug 2026 17:57:06 GMT",
    "lastModified": "2026-10-20T11:09:07.059Z",
    "protocolDesigner": "26.6.0",
    "source": "Protocol Designer",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.28"}

def run(protocol: protocol_api.ProtocolContext) -> None:
    # Load Labware:
    tip_rack_1 = protocol.load_labware(
        "opentrons_96_tiprack_300ul",
        location="10",
        label="Opentrons OT-2 96 Tip Rack 300 µL (1)",
        namespace="opentrons",
        version=1,
    )
    tube_rack_1 = protocol.load_labware_from_definition(
        CUSTOM_LABWARE["custom_beta/opentrons_15_tuberack_14000ul/1"],
        location="1",
    )
    well_plate_1 = protocol.load_labware_from_definition(
        CUSTOM_LABWARE["custom_beta/staining_jar/1"],
        location="3",
    )

    # Load Pipettes:
    pipette_right = protocol.load_instrument("p300_single_gen2", "right")

    # Define Liquids:
    liquid_1 = protocol.define_liquid(
        "staining_liquid",
        display_color="#b925ffff",
    )

    # Load Liquids:
    tube_rack_1.load_liquid(
        wells=["C1"],
        liquid=liquid_1,
        volume=10000,
    )

    # PROTOCOL STEPS

    # Step 1: transfer
    pipette_right.transfer_with_liquid_class(
        volume=150,
        source=[tube_rack_1["C1"], tube_rack_1["C1"]],
        dest=[well_plate_1["B1"], well_plate_1["B2"]],
        new_tip="once",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_1",
            properties={"p300_single_gen2": {"opentrons/opentrons_96_tiprack_300ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 46.4)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 46.4)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 0)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_right.drop_tip()

CUSTOM_LABWARE = json.loads("""{"custom_beta/opentrons_15_tuberack_14000ul/1":{"ordering":[["A1","B1","C1"],["A2","B2","C2"],["A3","B3","C3"],["A4","B4","C4"],["A5","B5","C5"]],"brand":{"brand":"Opentrons","brandId":[]},"metadata":{"displayName":"Opentrons 15 Tube Rack with Generic 14 mL","displayCategory":"tubeRack","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.76,"yDimension":85.48,"zDimension":125},"wells":{"A1":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":13.88,"y":67.74,"z":7},"B1":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":13.88,"y":42.74,"z":7},"C1":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":13.88,"y":17.74,"z":7},"A2":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":38.88,"y":67.74,"z":7},"B2":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":38.88,"y":42.74,"z":7},"C2":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":38.88,"y":17.74,"z":7},"A3":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":63.88,"y":67.74,"z":7},"B3":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":63.88,"y":42.74,"z":7},"C3":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":63.88,"y":17.74,"z":7},"A4":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":88.88,"y":67.74,"z":7},"B4":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":88.88,"y":42.74,"z":7},"C4":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":88.88,"y":17.74,"z":7},"A5":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":113.88,"y":67.74,"z":7},"B5":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":113.88,"y":42.74,"z":7},"C5":{"depth":118,"totalLiquidVolume":14000,"shape":"circular","diameter":15,"x":113.88,"y":17.74,"z":7}},"groups":[{"metadata":{"wellBottomShape":"v","displayCategory":"tubeRack"},"wells":["A1","B1","C1","A2","B2","C2","A3","B3","C3","A4","B4","C4","A5","B5","C5"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"opentrons_15_tuberack_14000ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}},"custom_beta/staining_jar/1":{"ordering":[["A1","B1","C1"],["A2","B2","C2"]],"brand":{"brand":"The real OT","brandId":[]},"metadata":{"displayName":"The Real Staining Jar","displayCategory":"wellPlate","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.5,"yDimension":85.2,"zDimension":130},"wells":{"A1":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":40,"y":42.5,"z":113.2},"B1":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":40,"y":21.3,"z":113.2},"C1":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":40,"y":0.1,"z":113.2},"A2":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":90,"y":42.5,"z":113.2},"B2":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":90,"y":21.3,"z":113.2},"C2":{"depth":16.8,"totalLiquidVolume":200,"shape":"rectangular","xDimension":20,"yDimension":0.1,"x":90,"y":0.1,"z":113.2}},"groups":[{"metadata":{"wellBottomShape":"v"},"wells":["A1","B1","C1","A2","B2","C2"]}],"parameters":{"format":"irregular","quirks":[],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"staining_jar"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":-3,"y":-3,"z":2}}}""")

DESIGNER_APPLICATION = """{"robot":{"model":"OT-2 Standard"},"designerApplication":{"name":"opentrons/protocol-designer","version":"2606.0.0","data":{"pipetteTiprackAssignments":{"77b84345-5ae8-440e-bf90-098c8b56f4c8":["opentrons/opentrons_96_tiprack_300ul/1"]},"dismissedWarnings":{"form":[],"timeline":[]},"ingredients":{"0":{"displayName":"staining_liquid","displayColor":"#b925ffff","description":null,"liquidGroupId":"0"}},"ingredLocations":{"5144ff12-ec14-44b0-bc69-b734c43ff881:custom_beta/opentrons_15_tuberack_14000ul/1":{"C1":{"0":{"volume":10000}}}},"savedStepForms":{"__INITIAL_DECK_SETUP_STEP__":{"stepType":"manualIntervention","id":"__INITIAL_DECK_SETUP_STEP__","labwareLocationUpdate":{"a3b56cd9-b483-45df-97e1-70c500039125:opentrons/opentrons_96_tiprack_300ul/1":"10","5144ff12-ec14-44b0-bc69-b734c43ff881:custom_beta/opentrons_15_tuberack_14000ul/1":"1","6cbd19b6-be0f-4a98-b7e2-5e7e37ff86f2:custom_beta/staining_jar/1":"3"},"pipetteLocationUpdate":{"77b84345-5ae8-440e-bf90-098c8b56f4c8":"right"},"moduleLocationUpdate":{},"moduleStateUpdate":{},"trashBinLocationUpdate":{"5c4df689-a5bd-4bc0-923f-851aed16cb08:trashBin":"cutout12"},"wasteChuteLocationUpdate":{},"stagingAreaLocationUpdate":{},"gripperLocationUpdate":{}},"2d98c3c3-3f31-4e8b-858e-0c4605ecfa43":{"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"46.4","aspirate_labware":"5144ff12-ec14-44b0-bc69-b734c43ff881:custom_beta/opentrons_15_tuberack_14000ul/1","aspirate_mix_checkbox":false,"aspirate_mix_times":"","aspirate_mix_volume":null,"aspirate_mmFromBottom":null,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["C1"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"46.4","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"once","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"46.4","dispense_labware":"6cbd19b6-be0f-4a98-b7e2-5e7e37ff86f2:custom_beta/staining_jar/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":null,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["B1","B2"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"5c4df689-a5bd-4bc0-923f-851aed16cb08:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":null,"path":"single","pipette":"77b84345-5ae8-440e-bf90-098c8b56f4c8","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":false,"pushOut_volume":"0","tipRack":"opentrons/opentrons_96_tiprack_300ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"150","id":"2d98c3c3-3f31-4e8b-858e-0c4605ecfa43","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0}},"orderedStepIds":["2d98c3c3-3f31-4e8b-858e-0c4605ecfa43"],"pipettes":{"77b84345-5ae8-440e-bf90-098c8b56f4c8":{"pipetteName":"p300_single_gen2"}},"modules":{},"labware":{"a3b56cd9-b483-45df-97e1-70c500039125:opentrons/opentrons_96_tiprack_300ul/1":{"displayName":"Opentrons OT-2 96 Tip Rack 300 µL (1)","labwareDefURI":"opentrons/opentrons_96_tiprack_300ul/1"},"5144ff12-ec14-44b0-bc69-b734c43ff881:custom_beta/opentrons_15_tuberack_14000ul/1":{"displayName":"Opentrons 15 Tube Rack with Generic 14 mL","labwareDefURI":"custom_beta/opentrons_15_tuberack_14000ul/1"},"6cbd19b6-be0f-4a98-b7e2-5e7e37ff86f2:custom_beta/staining_jar/1":{"displayName":"The Real Staining Jar","labwareDefURI":"custom_beta/staining_jar/1"}}}},"metadata":{"protocolName":"staining_show_protocol","author":"Stephan Becker openUC2","description":"a show protocol which visualize the stainstorm staining process","source":"Protocol Designer","created":1790593704850,"lastModified":1792494547059}}"""
