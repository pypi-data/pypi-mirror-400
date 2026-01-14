import threefive3
from bpkio_cli.utils.scte35 import get_descriptor_type
from bpkio_cli.writers.colorizer import Colorizer as CL
from lxml import etree


def summarize(payload, separator="  "):
    if isinstance(payload, threefive3.Cue):
        cue = payload
    else:
        cue = threefive3.Cue(payload)
        cue.decode()

    lines = []

    extracted = None
    match cue.info_section.splice_command_type:
        case 5:
            extracted = dict(
                command=f"{cue.command.name} ({cue.command.command_type})",
                event_id=cue.command.splice_event_id,
                duration=cue.command.break_duration,
                avail=f"{cue.command.avail_num}/{cue.command.avails_expected}",
            )
        case 6:
            extracted = dict(command=f"{cue.command.name} ({cue.command.command_type})")
    if extracted:
        lines.append(
            separator.join(
                [
                    CL.labeled(v, label=label, label_style=CL.bic_label)
                    for label, v in extracted.items()
                ]
            )
        )

    for d in cue.descriptors:
        if d.tag != 0:
            extracted = dict()

            extracted["descriptor"] = (
                f"{CL.high3_rev(d.segmentation_message) or '(Unknown)'} "
                f"({d.segmentation_type_id} | {hex(d.segmentation_type_id)})"
            )

            extracted["event_id"] = int(d.segmentation_event_id, 16)
            if d.segmentation_duration_flag:
                extracted["duration"] = d.segmentation_duration

            if d.segmentation_upid_type > 0:
                if d.segmentation_upid_type == 12:
                    extracted["upid_fmt"] = d.segmentation_upid["format_identifier"]
                    extracted["upid"] = d.segmentation_upid["private_data"]
                else:
                    extracted["upid"] = d.segmentation_upid

                # decode it from hex
                try:
                    extracted["upid"] = bytes.fromhex(extracted["upid"][2:]).decode(
                        "utf-8"
                    )
                except UnicodeDecodeError:
                    pass

            if hasattr(d, "segments_expected"):
                extracted["segments"] = f"{d.segment_num}/{d.segments_expected}"

            lines.append(
                separator.join(
                    [CL.labeled(v, label=label) for label, v in extracted.items()]
                )
            )

    return lines


def summarize_xml(element: etree._Element, separator="  "):
    # TODO - rewrite on the basis of using mpd-inspector

    SCTE35_NAMESPACE = "http://www.scte.org/schemas/35/2016"

    lines = []
    try:
        # TODO - accept other namespaces?
        if element.tag != f"{{{SCTE35_NAMESPACE}}}SpliceInfoSection":
            return [CL.error("Unknown SCTE-35 XML element")]

        # First element is the command type
        command_type = element[0]
        extracted = None
        match command_type.tag.replace(f"{{{SCTE35_NAMESPACE}}}", ""):
            case "SpliceInsert":
                extracted = dict(
                    command="SpliceInsert (5)",
                    # event_id=cue.command.splice_event_id,
                    # duration=cue.command.break_duration,
                    # avail=f"{cue.command.avail_num}/{cue.command.avails_expected}",
                )
            case "TimeSignal":
                extracted = dict(command="TimeSignal (6)")

        if extracted:
            lines.append(
                separator.join(
                    [
                        CL.labeled(v, label=label, label_style=CL.bic_label)
                        for label, v in extracted.items()
                    ]
                )
            )

        # Descriptors
        for d in element.findall(f"{{{SCTE35_NAMESPACE}}}SegmentationDescriptor"):
            extracted = dict()

            extracted["descriptor"] = (
                f"{CL.high3_rev(get_descriptor_type(int(d.get('segmentationTypeId'))).label) or '(Unknown)'} "
                f"({d.get('segmentationTypeId')} | {hex(int(d.get('segmentationTypeId')))})"
            )

            extracted["event_id"] = d.get("segmentationEventId")
            extracted["duration"] = int(d.get("segmentationDuration", 0)) / 90000

            upid = d.find(f"{{{SCTE35_NAMESPACE}}}SegmentationUpid")
            if upid is not None:
                if int(upid.get("segmentationUpidType")) > 0:
                    extracted["upid"] = upid.text
                    if (
                        int(upid.get("segmentationUpidType")) == 12
                        and upid.get("segmentationUpidFormat") == "hexbinary"
                    ):
                        extracted["upid_fmt"] = bytes.fromhex(
                            extracted["upid"][:8]
                        ).decode("utf-8")
                        extracted["upid"] = bytes.fromhex(extracted["upid"][8:]).decode(
                            "utf-8"
                        )
                    else:
                        pass

            extracted["segments"] = f"{d.get('segmentNum')}/{d.get('segmentsExpected')}"

            lines.append(
                separator.join(
                    [CL.labeled(v, label=label) for label, v in extracted.items()]
                )
            )

        return lines
    except Exception as e:
        return [CL.error("Unparsable")]
