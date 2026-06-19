"""
PDF eksport — A4 formatda rasmiy prognoz hujjati.
Matplotlib PdfPages yordamida.
"""
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def export_forecast_pdf(forecast_images, telegram_texts, comment="",
                        output_path="static/output/prognoz.pdf"):
    """
    3 kunlik prognozni PDF formatda eksport qiladi.
    
    Args:
        forecast_images: 3 ta PNG fayl yo'llari
        telegram_texts: 3 ta Telegram matn
        comment: Umumiy izoh
        output_path: Chiqish fayl yo'li
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(output_path) as pdf:
        for i, img_path in enumerate(forecast_images):
            if not Path(img_path).exists():
                continue

            fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
            fig.set_facecolor("white")

            # Rasm
            img = plt.imread(img_path)
            ax = fig.add_axes([0.02, 0.05, 0.96, 0.90])
            ax.imshow(img)
            ax.axis("off")

            # Sahifa raqami
            fig.text(0.5, 0.01,
                f"Sahifa {i+1}/3  |  Gidrometeorologiya xizmati agentligi  |  hydromet.uz",
                fontsize=8, color="#78909c", ha="center")

            pdf.savefig(fig, dpi=150)
            plt.close(fig)

        # 4-sahifa: Telegram matn versiyasi
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 portrait
        fig.set_facecolor("white")
        ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
        ax.axis("off")

        ax.text(0.5, 0.98, "OB-HAVO PROGNOZI — MATN VERSIYASI",
                fontsize=14, fontweight="bold", color="#0d2137",
                ha="center", va="top", transform=ax.transAxes)

        full_text = "\n\n".join(telegram_texts)
        ax.text(0.02, 0.92, full_text, fontsize=9, color="#263238",
                va="top", transform=ax.transAxes,
                fontfamily="monospace", wrap=True)

        fig.text(0.5, 0.02,
            f"Yaratilgan: {datetime.now().strftime('%Y-%m-%d %H:%M')} | hydromet.uz",
            fontsize=8, color="#78909c", ha="center")

        pdf.savefig(fig, dpi=150)
        plt.close(fig)

    return output_path
