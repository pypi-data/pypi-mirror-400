def video2thumbnails(video_path: str, img_path_prefix: str, count=16):
    """
    Usage::

      video2thumbnails('./video.mp4', '/tmp/img_', count=10)

    will create files like `/tmp/img_004.png`
    """
    assert count < 1000
    import cv2

    v = cv2.VideoCapture(video_path)
    frames = v.get(cv2.CAP_PROP_FRAME_COUNT)
    assert frames > count
    for i in range(count):
        frame = int(frames * (i + 1) / (count + 1))
        v.set(cv2.CAP_PROP_POS_FRAMES, frame)  # just cue to 20 sec. position
        success, image = v.read()
        if success:
            cv2.imwrite(
                "%s%03d.png"
                % (
                    img_path_prefix,
                    i,
                ),
                image,
            )  # save frame as JPEG file
