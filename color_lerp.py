# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "py-imgui-redux>=6.2.0"
# ]
# ///
import imgui as im
from imgui_utils.boilerplate import window_mainloop
import math


def lerp(a: float, b: float, t: float) -> float:
    return (b - a) * t + a


def lerpRGB(c1: im.Vec4, c2: im.Vec4, t: float) -> im.Vec4:
    return (c2 - c1) * t + c1


def lerpHSV(c1: im.Vec4, c2: im.Vec4, t: float) -> im.Vec4:
    hsv1 = im.ColorConvertRGBtoHSV(c1)
    hsv2 = im.ColorConvertRGBtoHSV(c2)
    outHSV = lerpRGB(hsv1, hsv2, t)

    return im.ColorConvertHSVtoRGB(outHSV)


def rgb2hsl(rgb: im.Vec4) -> im.Vec4:
    r = rgb.x
    g = rgb.y
    b = rgb.z
    xMax = max(r, g, b)
    xMin = min(r, g, b)
    c = xMax - xMin
    l = (xMax + xMin) / 2
    h = 0
    if c == 0:
        h = 0
    elif xMax == r:
        _x = (g - b) / c
        _x %= 6
        h = 60 * _x
    elif xMax == g:
        _x = (b - r) / c
        _x += 2
        h = 60 * _x
    elif xMax == b:
        _x = (r - g) / c
        _x += 4
        h = 60 * _x

    if l == 0 or l == 1:
        s = 0
    else:
        s = (xMax - l) / min(l, 1 - l)

    return im.Vec4(h, s, l, 1.0)


def hsl2rgb(hsl: im.Vec4) -> im.Vec4:
    h = hsl.x
    s = hsl.y
    l = hsl.z

    a = s * min(l, 1 - l)

    def f(n: float) -> float:
        k = (n + h / 30) % 12
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    r = f(0)
    g = f(8)
    b = f(4)

    return im.Vec4(r, g, b, 1.0)


def lerpHSL(c1: im.Vec4, c2: im.Vec4, t: float) -> im.Vec4:
    hsl1 = rgb2hsl(c1)
    hsl2 = rgb2hsl(c2)

    outHsl = lerpRGB(hsl1, hsl2, t)

    return hsl2rgb(outHsl)


def smartLerpHSV(c1: im.Vec4, c2: im.Vec4, t: float) -> im.Vec4:
    h1, s1, v1 = im.ColorConvertRGBtoHSV(c1.x, c1.y, c1.z)
    h2, s2, v2 = im.ColorConvertRGBtoHSV(c2.x, c2.y, c2.z)

    if (h1 < h2):
        if abs(h1 + 1.0 - h2) < abs(h1 - h2):
            h1 += 1.0
    elif abs(h2 + 1.0 - h1) < abs(h1 - h2):
        h2 += 1.0

    hsv1 = im.Vec4(h1, s1, v1, 1.0)
    hsv2 = im.Vec4(h2, s2, v2, 1.0)

    outHSV = lerpRGB(hsv1, hsv2, t)

    if (outHSV.x > 1.0):
        outHSV.x -= 1

    r, g, b = im.ColorConvertHSVtoRGB(outHSV.x, outHSV.y, outHSV.z)
    return im.Vec4(r, g, b, 1.0)


def smartLerpHSL(c1: im.Vec4, c2: im.Vec4, t: float) -> im.Vec4:
    hsl1 = rgb2hsl(c1)
    hsl2 = rgb2hsl(c2)

    if (hsl1.x < hsl2.x):
        if abs(hsl1.x + 360.0 - hsl2.x) < abs(hsl1.x - hsl2.x):
            hsl1.x += 360.0
    elif abs(hsl2.x + 360.0 - hsl1.x) < abs(hsl1.x - hsl2.x):
        hsl2.x += 360.0

    outHSL = lerpRGB(hsl1, hsl2, t)

    if (outHSL.x > 360.0):
        outHSL.x -= 360

    return hsl2rgb(outHSL)


def linear(t: float) -> float:
    return t


def easeInOutSine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def easeInOutCubic(x: float) -> float:
    if x < 0.5:
        return 4 * x * x * x

    return 1 - math.pow(-2 * x + 2, 3) / 2


def easeInOutCirc(x: float) -> float:
    if x < 0.5:
        return (1 - math.sqrt(1 - math.pow(2 * x, 2))) / 2

    return (math.sqrt(1 - math.pow(-2 * x + 2, 2)) + 1) / 2


BOX_HEIGHT = 50
CIRCLE_RADIUS = 100
DOT_RADIUS = 10

CIRCLE_COL = im.Vec4(1.0, 1.0, 1.0, 1.0).toColorU32()


class LerpTest:

    def __init__(self) -> None:
        self.numVals = im.IntRef(30)
        self.startColor = im.Vec4(0, 0, 0, 1.0)
        self.endColor = im.Vec4(1.0, 1.0, 1.0, 1.0)

        self.useSquares = im.BoolRef(False)

        self.selectedEase = 0
        self.easings = [
            ("linear", linear), ("easeInOutSine", easeInOutSine), ("easeInOutCubic", easeInOutCubic),
            ("easeInOutCirc", easeInOutCirc)
        ]

    def init(self):
        pass

    def renderPreview(self, label: str, lerpFunc):
        im.Text(label)
        startPos = im.GetCursorScreenPos()

        windowWidth = im.GetWindowWidth() / 2 - im.GetStyle().WindowPadding.x * 2

        dl = im.GetWindowDrawList()

        boxWidth = windowWidth / self.numVals.val

        satCircleCenter = im.Vec2(startPos.x + CIRCLE_RADIUS, startPos.y + BOX_HEIGHT + CIRCLE_RADIUS + 30)

        valCircleCenter = im.Vec2(satCircleCenter.x + CIRCLE_RADIUS * 2 + 30, satCircleCenter.y)

        if self.useSquares.val:
            p1 = im.Vec2(valCircleCenter.x - CIRCLE_RADIUS, valCircleCenter.y - CIRCLE_RADIUS)
            p2 = im.Vec2(valCircleCenter.x + CIRCLE_RADIUS, valCircleCenter.y + CIRCLE_RADIUS)
            dl.AddRectFilled(p1, p2, CIRCLE_COL, DOT_RADIUS)

            p1 = im.Vec2(satCircleCenter.x - CIRCLE_RADIUS, satCircleCenter.y - CIRCLE_RADIUS)
            p2 = im.Vec2(satCircleCenter.x + CIRCLE_RADIUS, satCircleCenter.y + CIRCLE_RADIUS)
            dl.AddRectFilled(p1, p2, CIRCLE_COL, DOT_RADIUS)
        else:
            dl.AddCircleFilled(satCircleCenter, CIRCLE_RADIUS, CIRCLE_COL)
            dl.AddCircleFilled(valCircleCenter, CIRCLE_RADIUS, CIRCLE_COL)

        dl.AddText(im.Vec2(satCircleCenter.x - 20, satCircleCenter.y - CIRCLE_RADIUS - 15), 0xFFFFFFFF, "Saturation")
        dl.AddText(im.Vec2(valCircleCenter.x - 20, valCircleCenter.y - CIRCLE_RADIUS - 15), 0xFFFFFFFF, "Value")

        for i in range(self.numVals.val):
            p1 = im.Vec2(startPos.x + i * boxWidth, startPos.y)
            p2 = im.Vec2(startPos.x + (i + 1) * boxWidth, startPos.y + BOX_HEIGHT)

            t = i / self.numVals.val
            t = self.easings[self.selectedEase][1](t)

            color = lerpFunc(self.startColor, self.endColor, t)
            cInt = im.ColorConvertFloat4ToU32(color)

            dl.AddRectFilled(p1, p2, cInt, 0)

            h, s, v = im.ColorConvertRGBtoHSV(color.x, color.y, color.z)

            if self.useSquares.val:
                originX = satCircleCenter.x - CIRCLE_RADIUS + DOT_RADIUS
                # invert Y
                originY = satCircleCenter.y + CIRCLE_RADIUS - DOT_RADIUS

                usableW = (CIRCLE_RADIUS * 2) - (DOT_RADIUS * 2)

                x = h * usableW
                y = s * usableW

                dl.AddCircleFilled(im.Vec2(originX + x, originY - y), DOT_RADIUS, cInt)

                originX = valCircleCenter.x - CIRCLE_RADIUS + DOT_RADIUS
                y = v * usableW

                dl.AddCircleFilled(im.Vec2(originX + x, originY - y), DOT_RADIUS, cInt)
            else:
                hRad = math.radians(h * 360)

                usableRadius = CIRCLE_RADIUS - DOT_RADIUS

                p = im.Vec2(s * math.cos(hRad) * usableRadius, s * math.sin(hRad) * usableRadius)
                dl.AddCircleFilled(satCircleCenter + p, DOT_RADIUS, cInt)

                p = im.Vec2(v * math.cos(hRad) * usableRadius, v * math.sin(hRad) * usableRadius)
                dl.AddCircleFilled(valCircleCenter + p, DOT_RADIUS, cInt)

        im.SetCursorScreenPos(im.Vec2(startPos.x, satCircleCenter.y + CIRCLE_RADIUS + 10))
        im.Dummy(im.Vec2())

    def render(self) -> bool:
        if im.Begin("Settings"):
            im.SetNextItemWidth(100)
            im.InputInt("Num Vals", self.numVals)
            if im.BeginListBox("Ease Func"):
                for idx, e in enumerate(self.easings):
                    if im.Selectable(e[0], self.selectedEase == idx):
                        self.selectedEase = idx
                im.EndListBox()
            im.CheckBox("Use Squares", self.useSquares)
            im.SetNextItemWidth(300)
            im.ColorPicker3("Start", self.startColor, im.ColorEditFlags.PickerHueBar)
            im.SetNextItemWidth(300)
            im.ColorPicker3("End", self.endColor, im.ColorEditFlags.PickerHueBar)

        im.End()

        if im.Begin("Preview"):
            if im.BeginTable("Previews", 2):
                im.TableNextColumn()
                self.renderPreview("RGB", lerpRGB)
                im.TableNextColumn()

                im.TableNextColumn()
                self.renderPreview("HSV", lerpHSV)
                im.TableNextColumn()
                self.renderPreview("Smart HSV", smartLerpHSV)
                im.TableNextColumn()
                self.renderPreview("HSL", lerpHSL)
                im.TableNextColumn()
                self.renderPreview("Smart HSL", smartLerpHSL)

                im.EndTable()

        im.End()

        return False


test = LerpTest()
window_mainloop("Lerp", test.render, init=test.init)
