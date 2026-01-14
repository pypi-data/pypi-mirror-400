import json
import pathlib

from .html import generateHtml

def advancedArgs(f):
    # Note that some of these are string arguments. If the string is a single number it applies
    # for all cameras/pairs, but parameters can also be defined for individual cameras/pairs
    # using the following syntax (spaces are optional):
    #
    #   --parameter "camera = value, camera = value, _ = value"
    #
    # * where ',' separates a number of camera-value pairs,
    # * for monocular parameters each "camera" key is a number 0, 1, 2, … , 9
    # * for stereo parameters it is comma-separate pair 01, 02, 12, … (smaller number first)
    # * the camera key "_" defines default used for cameras whose key is not defined
    # * "value" is the parameter value
    #
    # Thresholds for passing checks.
    f("--coverage_threshold_monocular", default="0.8", help="Coverage check pass threshold")
    f("--coverage_threshold_stereo", default="0.7", help="Coverage check pass threshold")
    f("--reprojection_threshold", default="0.8", help="Reprojection check pass threshold for camera phase")
    f("--reprojection_threshold_imu", default="1.5", help="Reprojection check pass threshold for IMU phase")
    f("--reprojection_threshold_stereo", default="0.8", help="Reprojection check pass threshold for camera phase (stereo overlap)")
    f("--reprojection_threshold_imu_stereo", default="1.5", help="Reprojection check pass threshold for IMU phase (stereo overlap)")
    # You can probably leave these to the default values.
    f("--bucket_count_vertical", type=int, default=10, help="Coverage check resolution")
    f("--bucket_full_count_monocular", type=int, default=30, help="Coverage check bucket threshold")
    f("--bucket_full_count_stereo", type=int, default=20, help="Coverage check bucket threshold")
    f("--camera_max_rel_position_change", type=float, default=0.05, help="Extrinsics check relative camera-to-camera position change threshold")
    f("--imu_max_rel_position_change", type=float, default=0.2, help="Extrinsics check relative IMU-to-camera position change threshold")
    f("--camera_max_angle_change_degrees", type=float, default=1, help="Extrinsics check camera angle change threshold")
    f("--verbose_report", default=False, action="store_true", help="Add extra details to HTML report.")

def define_args(parser, include_advanced=False):
    parser.add_argument("--output_html", type=pathlib.Path, help="Path to calibration report HTML output.")
    parser.add_argument("--output_json", type=pathlib.Path, help="Path to JSON output.")

    if include_advanced:
        def f(name, **kwargs):
            parser.add_argument(name, **kwargs)
        advancedArgs(f)

def addDefaultsForAdvanced(args):
    def f(name, default, **kwargs):
        _, __, withoutDashes = name.partition('--')
        assert len(withoutDashes) > 0
        if not hasattr(args, withoutDashes):
            setattr(args, withoutDashes, default)
    advancedArgs(f)

def getCameraParameter(args, name, cameraInds):
    vargs = vars(args)
    definition = vargs[name]
    try:
        return float(definition) # Single number used for all cameras.
    except:
        pass

    if isinstance(cameraInds, int): cameraInds = [cameraInds]
    cameraInds = cameraInds.copy()
    cameraInds.sort()
    for i in cameraInds: assert(i >= 0 and i <= 9)

    key = "".join([str(x) for x in cameraInds])

    pairs = definition.split(",")
    default = None
    for pair in pairs:
        tokens = pair.split("=")
        k = tokens[0].strip()
        value = float(tokens[1].strip())
        assert(len(tokens) == 2)
        if k == "_": default = value
        elif k == key: return value
    if default is None:
        raise Exception(f"Could not determine parameter value of `{name}` for camera key `{key}`.")
    return default

def getReprojectionThresholds(args, cameraInds):
    if len(cameraInds) == 2:
        keyCam = "reprojection_threshold_stereo"
        keyImu = "reprojection_threshold_imu_stereo"
    else:
        keyCam = "reprojection_threshold"
        keyImu = "reprojection_threshold_imu"
    reprojection_threshold = getCameraParameter(args, keyCam, cameraInds)
    reprojection_threshold_imu = getCameraParameter(args, keyImu, cameraInds)
    return reprojection_threshold, reprojection_threshold_imu

def clamp(x, minValue, maxValue):
    if x < minValue: return minValue
    if x > maxValue: return maxValue
    return x

def readJson(filePath):
    with open(filePath) as f:
        return json.load(f)

def radToDeg(a):
    import numpy as np
    return a / np.pi * 180

def angle(vec1, vec2):
    import numpy as np
    return np.arccos(np.dot(vec1, vec2))

def computeVergenceDegrees(imuToCam0, imuToCam1):
    # Principal axis in IMU coordinates
    def axis(imuToCam):
        camToImuRot = imuToCam[:3, :3].transpose()
        return camToImuRot[:, 2]
    return radToDeg(angle(axis(imuToCam0), axis(imuToCam1)))

def computeBaseline(imuToCam0, imuToCam1):
    import numpy as np
    cam0ToCam1 = imuToCam1 @ np.linalg.inv(imuToCam0)
    return np.linalg.norm(cam0ToCam1[:3, 3])

def base64(fig):
    import matplotlib.pyplot as plt
    import io
    import base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def scatterReprojection(xy, errors, width, height, threshold):
    import matplotlib.pyplot as plt
    import numpy as np
    errors = np.minimum(errors, threshold)

    fig, ax = plt.subplots()
    rect = np.array([[0, 0], [width, 0], [width, height], [0, height], [0, 0]])
    if xy.size > 0:
        ax.scatter(xy[:, 0], xy[:, 1], c=errors, marker="o", alpha=0.3, s=2, cmap="jet")
    ax.plot(rect[:, 0], rect[:, 1], color="black", linewidth=2)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("equal")
    ax.axis("off")
    ax.margins(x=0, y=0)
    fig.tight_layout()
    image = base64(fig)
    plt.close(fig)
    return image

def bucketCount(args, xy, width, height, fullCount):
    import matplotlib.pyplot as plt
    import numpy as np
    bucketCountHorizontal = round(width / height * args.bucket_count_vertical)

    v = np.zeros(shape=(args.bucket_count_vertical, bucketCountHorizontal))

    for i in range(xy.shape[0]):
        x = clamp(int(xy[i, 0] / width * bucketCountHorizontal), 0, bucketCountHorizontal - 1)
        y = clamp(int(xy[i, 1] / height * args.bucket_count_vertical), 0, args.bucket_count_vertical - 1)
        v[y, x] += 1

    v = np.minimum(v, fullCount)
    coverage = np.sum(v == fullCount) / (bucketCountHorizontal * args.bucket_count_vertical)
    v /= fullCount

    fig, ax = plt.subplots()
    ax.imshow(v, cmap='gray', origin='upper', vmin=0, vmax=1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.margins(x=0, y=0)
    fig.tight_layout()
    image = base64(fig)
    plt.close(fig)
    return coverage, image

def appendCoverage(output, cameraInds, images, ret, threshold):
    if not "coverage" in output: output["coverage"] = []
    passed = bool(ret >= threshold)
    output["coverage"].append({
        "cameraInds": cameraInds,
        "images": images,
        "bucketsCoverage": ret,
        "threshold": threshold,
        "passed": passed,
    })
    if not passed: output["passed"] = False

def appendReprojection(args, output, cameraInds, images, errorCam, errorCamImu):
    key = "reprojection"
    if not key in output: output[key] = []

    reprojection_threshold, reprojection_threshold_imu = getReprojectionThresholds(args, cameraInds)

    passedCam = bool(errorCam < reprojection_threshold)
    passedCamImu = bool(errorCamImu is None or errorCamImu < reprojection_threshold_imu)
    passed = passedCam and passedCamImu
    output[key].append({
        "cameraInds": cameraInds,
        "images": images,
        "errorCam": errorCam,
        "errorCamImu": errorCamImu,
        "thresholdCam": reprojection_threshold,
        "thresholdCamImu": reprojection_threshold_imu,
        "passed": passed,
    })
    if not passed: output["passed"] = False

def mergeCoordinates(data, cameraInd, xKey, yKey, requiredKey=None):
    import numpy as np
    x = []
    y = []
    for frame in data:
        if frame["camera_ind"] != cameraInd: continue
        if requiredKey and requiredKey not in frame: continue
        x.extend(frame[xKey])
        y.extend(frame[yKey])
    assert(len(x) == len(y))
    return np.vstack((np.array(x), np.array(y))).transpose()

def mergeErrors(data, cameraInd, key):
    import numpy as np
    errors = []
    for frame in data:
        if frame["camera_ind"] != cameraInd: continue
        if not key in frame: continue
        errors.extend(frame[key])
    return np.array(errors)

def computeReprojection(args, xy, xyImu, errorsCam, errorsCamImu, width, height, cameraInds):
    reprojection_threshold, reprojection_threshold_imu = getReprojectionThresholds(args, cameraInds)
    image0 = scatterReprojection(xy, errorsCam, width, height, reprojection_threshold)
    meanErrorCam = errorsCam.mean() if errorsCam.size > 0 else 0

    meanErrorCamImu = None
    images = [image0]
    if len(errorsCamImu) > 0:
        image1 = scatterReprojection(xyImu, errorsCamImu, width, height, reprojection_threshold_imu)
        meanErrorCamImu = errorsCamImu.mean() if errorsCamImu.size > 0 else 0
        images.append(image1)

    return images, meanErrorCam, meanErrorCamImu

def computeCamera(args, data, detectedDict, width, height, cameraInd, output):
    import numpy as np

    # Metrics and visualizations for this camera alone.
    xy = mergeCoordinates(data, cameraInd, "detected_px", "detected_py")
    xyImu = mergeCoordinates(data, cameraInd, "detected_px", "detected_py", "error_cam_imu")

    ret, image1 = bucketCount(args, xy, width, height, args.bucket_full_count_monocular)
    appendCoverage(output, [cameraInd], [image1], ret, getCameraParameter(args, "coverage_threshold_monocular", cameraInd))

    errorsCam = mergeErrors(data, cameraInd, "error_cam")
    errorsCamImu = mergeErrors(data, cameraInd, "error_cam_imu")
    images, meanErrorCam, meanErrorCamImu = computeReprojection(args, xy, xyImu, errorsCam, errorsCamImu, width, height, [cameraInd])
    appendReprojection(args, output, [cameraInd], images, meanErrorCam, meanErrorCamImu)

    # Handle camera pairs.
    for cameraInd0 in range(cameraInd):
        xy = []
        xy0 = []
        xyImu = []
        xyImu0 = []
        errorsCam = []
        errorsCam0 = []
        errorsCamImu = []
        errorsCamImu0 = []
        for frame in data:
            if frame["camera_ind"] != cameraInd: continue
            frameInd = frame["frame_ind"]
            for i, cornerId in enumerate(frame["corner_ids"]):
                detected = detectedDict.get((cameraInd0, frameInd, cornerId))
                if detected is None: continue
                xy0.append(detected["xy"])
                xy.append([frame["detected_px"][i], frame["detected_py"][i]])
                errorsCam0.append(detected["error_cam"])
                errorsCam.append(frame["error_cam"][i])
                if "error_cam_imu" not in detected or "error_cam_imu" not in frame: continue
                xyImu0.append(detected["xy"])
                xyImu.append([frame["detected_px"][i], frame["detected_py"][i]])
                errorsCamImu0.append(detected["error_cam_imu"])
                errorsCamImu.append(frame["error_cam_imu"][i])
        xy = np.array(xy)
        xyImu = np.array(xyImu)
        xy0 = np.array(xy0)
        xyImu0 = np.array(xyImu0)
        errorsCam = np.array(errorsCam)
        errorsCam0 = np.array(errorsCam0)
        errorsCamImu = np.array(errorsCamImu)
        errorsCamImu0 = np.array(errorsCamImu0)

        coverage_threshold_stereo = getCameraParameter(args, "coverage_threshold_stereo", [cameraInd0, cameraInd])

        ret, image1 = bucketCount(args, xy, width, height, args.bucket_full_count_stereo)
        appendCoverage(output, [cameraInd0, cameraInd], [image1], ret, coverage_threshold_stereo)

        ret, image1 = bucketCount(args, xy0, width, height, args.bucket_full_count_stereo)
        appendCoverage(output, [cameraInd, cameraInd0], [image1], ret, coverage_threshold_stereo)

        cameraInds = [cameraInd0, cameraInd]
        images, meanErrorCam, meanErrorCamImu = computeReprojection(args, xy, xyImu, errorsCam, errorsCamImu, width, height, cameraInds)
        appendReprojection(args, output, cameraInds, images, meanErrorCam, meanErrorCamImu)

        cameraInds = [cameraInd, cameraInd0]
        images, meanErrorCam, meanErrorCamImu = computeReprojection(args, xy0, xyImu0, errorsCam0, errorsCamImu0, width, height, cameraInds)
        appendReprojection(args, output, cameraInds, images, meanErrorCam, meanErrorCamImu)

def computeExtrinsicsChecks(args, report_data, calibration, output):
    import numpy as np
    cameraCount = len(calibration["cameras"])
    if cameraCount == 2:
        imuToCam0 = np.array(calibration["cameras"][0]["imuToCamera"])
        imuToCam1 = np.array(calibration["cameras"][1]["imuToCamera"])
        output["vergence_degrees"] = computeVergenceDegrees(imuToCam0, imuToCam1)
        output["baseline_mm"] = 1000 * computeBaseline(imuToCam0, imuToCam1)

    if not "base_calibration" in report_data: return
    baseCalibration = report_data["base_calibration"]
    if len(baseCalibration["cameras"]) != cameraCount:
        print("Base calibration camera count does not match calibration.")
        return

    if cameraCount == 2:
        baseImuToCam0 = np.array(baseCalibration["cameras"][0]["imuToCamera"])
        baseImuToCam1 = np.array(baseCalibration["cameras"][1]["imuToCamera"])
        output["base_calibration_vergence_degrees"] = computeVergenceDegrees(baseImuToCam0, baseImuToCam1)
        output["base_calibration_baseline_mm"] = 1000 * computeBaseline(baseImuToCam0, baseImuToCam1)

    def getImuToCam(calibration, cameraInd):
        return np.array(calibration["cameras"][cameraInd]["imuToCamera"])

    def updatePassed(output, passed):
        if not passed:
            output["extrinsics"]["passed"] = False
            output["passed"] = False

    def angle(R):
        return np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))

    output["extrinsics"] = {
        "passed": True,
        "pairs": [],
    }
    # IMU-to-camera changes.
    for cameraInd in range(cameraCount):
        imuToCam = getImuToCam(calibration, cameraInd)
        baseImuToCam = getImuToCam(baseCalibration, cameraInd)
        camPos = np.linalg.inv(imuToCam)[:3, 3]
        baseCamPos = np.linalg.inv(baseImuToCam)[:3, 3]
        d = np.linalg.norm(camPos - baseCamPos)
        thresholdDist = args.imu_max_rel_position_change * np.linalg.norm(baseCamPos)
        passed = d < thresholdDist
        output["extrinsics"]["pairs"].append({
            "cameraInds": [cameraInd],
            "distance_mm": 1000 * d,
            "threshold_mm": 1000 * thresholdDist,
            "passed": passed,
        })
        updatePassed(output, passed)

        a = angle(imuToCam[:3, :3] @ baseImuToCam[:3, :3].transpose())
        passed = a < args.camera_max_angle_change_degrees
        output["extrinsics"]["pairs"].append({
            "cameraInds": [cameraInd],
            "angle_degrees": a,
            "threshold_degrees": args.camera_max_angle_change_degrees,
            "passed": passed,
        })
        updatePassed(output, passed)

    # Camera-to-camera changes.
    for i1 in range(cameraCount):
        for i0 in range(i1):
            cam1ToCam0 = getImuToCam(calibration, i0) @ np.linalg.inv(getImuToCam(calibration, i1))
            baseCam1ToCam0 = getImuToCam(baseCalibration, i0) @ np.linalg.inv(getImuToCam(baseCalibration, i1))
            cam1Pos = cam1ToCam0[:3, 3]
            baseCam1Pos = baseCam1ToCam0[:3, 3]
            d = np.linalg.norm(cam1Pos - baseCam1Pos)
            thresholdDist = args.camera_max_rel_position_change * np.linalg.norm(baseCam1Pos)
            passed = d < thresholdDist
            output["extrinsics"]["pairs"].append({
                "cameraInds": [i0, i1],
                "distance_mm": 1000 * d,
                "threshold_mm": 1000 * thresholdDist,
                "passed": passed,
            })
            updatePassed(output, passed)

            a = angle(cam1ToCam0[:3, :3] @ baseCam1ToCam0[:3, :3].transpose())
            passed = a < args.camera_max_angle_change_degrees
            output["extrinsics"]["pairs"].append({
                "cameraInds": [i0, i1],
                "angle_degrees": a,
                "threshold_degrees": args.camera_max_angle_change_degrees,
                "passed": passed,
            })
            updatePassed(output, passed)

def generateReport(args, report_data, calibration):
    import numpy as np
    addDefaultsForAdvanced(args)
    width = calibration["cameras"][0]["imageWidth"]
    height = calibration["cameras"][0]["imageHeight"]

    output = { "width": width, "height": height, "passed": True }

    computeExtrinsicsChecks(args, report_data, calibration, output)

    detectedDict = {}
    for frame in report_data["data"]:
        for i, cornerId in enumerate(frame["corner_ids"]):
            key = (frame["camera_ind"], frame["frame_ind"], cornerId)
            detectedDict[key] = {
                "xy": [frame["detected_px"][i], frame["detected_py"][i]],
                "error_cam": frame["error_cam"][i],
            }
            if "error_cam_imu" in frame:
                detectedDict[key]["error_cam_imu"] = frame["error_cam_imu"][i]

    for cameraInd in range(len(calibration["cameras"])):
        computeCamera(args, report_data["data"], detectedDict, width, height, cameraInd, output)

    if args.output_json:
        with open(args.output_json, "w") as f:
            f.write(json.dumps(output, indent=4))
        print("Generated JSON report data at:", args.output_json)

    if args.output_html:
        generateHtml(args, report_data, calibration, output, args.output_html)

def report(args, report_data_str):
    report_data = json.loads(report_data_str)
    generateReport(args, report_data["report"], report_data["calibration"])
