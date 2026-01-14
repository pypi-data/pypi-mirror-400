"""The module implements a reference GIOU association metric."""


def giou_lr_lr(seg1: tuple[float, float], seg2: tuple[float, float]) -> float:
    s1, e1 = seg1
    s2, e2 = seg2
    inter_s = max(s1, s2)
    inter_e = min(e1, e2)

    intersection = max(0.0, inter_e - inter_s)
    l1, l2 = e1 - s1, e2 - s2
    union = l1 + l2 - intersection
    if union <= 0:
        return 0.0

    iou = intersection / union

    c_s = min(s1, s2)
    c_e = max(e1, e2)
    c_len = max(0.0, c_e - c_s)

    assert c_len > 0

    giou = iou - (c_len - union) / c_len
    return float((giou + 1) / 2.0)


def giou_ps_ps(ps1: tuple[float, float], ps2: tuple[float, float]) -> float:
    hs1 = ps1[1] / 2
    hs2 = ps2[1] / 2
    seg1 = ps1[0] - hs1, ps1[0] + hs1
    seg2 = ps2[0] - hs2, ps2[0] + hs2
    return giou_lr_lr(seg1, seg2)
