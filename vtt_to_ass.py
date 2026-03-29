import pysubs2

subs = pysubs2.load("subs.vtt")

subs.info["Title"] = "Locked Center Subtitles"

subs.styles.clear()

subs.styles["Default"] = pysubs2.SSAStyle(
    fontname="Montserrat",
    fontsize=36,
    primarycolor=pysubs2.Color(255, 255, 255),
    outlinecolor=pysubs2.Color(0, 0, 0),
    backcolor=pysubs2.Color(0, 0, 0),
    bold=True,
    outline=1,
    shadow=0,
    alignment=2,   # BOTTOM CENTER
    marginl=10,
    marginr=10,
    marginv=90
)

for line in subs:
    line.style = "Default"

subs.save("subs.ass")
