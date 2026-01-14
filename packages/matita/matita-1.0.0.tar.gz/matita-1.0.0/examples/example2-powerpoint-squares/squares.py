import random

from matita.office import powerpoint as pp

def squares():
    pp_app = pp.Application()
    pp_app.visible = True
    prs = pp_app.presentations.add()
    sld = prs.slides.Add(1, pp.ppLayoutBlank)

    for _ in range(1000):
        side = random.random() * prs.page_setup.slideheight / 3
        left = -side + random.random() * (side + prs.page_setup.slide_width)
        top = -side + random.random() * (side + prs.page_setup.slide_height)
        shp = sld.shapes.add_shape(pp.msoShapeRectangle, left, top, side, side)
        shp.line.visible = False
        shp.fill.fore_color.rgb = random.randint(0, 256 ** 3)
        eff = sld.timeline.main_sequence.add_effect(
            Shape=shp,
            effectId=pp.msoAnimEffectFly,
            Level=pp.msoAnimateLevelNone,
            trigger=pp.msoAnimTriggerAfterPrevious,
        )
        direction = random.choice([
            pp.msoAnimDirectionLeft,
            pp.msoAnimDirectionTop,
            pp.msoAnimDirectionRight,
            pp.msoAnimDirectionBottom
        ])
        eff.effect_parameters.direction = direction
        eff.timing.duration = 0.2

if __name__ == "__main__":
    squares()
