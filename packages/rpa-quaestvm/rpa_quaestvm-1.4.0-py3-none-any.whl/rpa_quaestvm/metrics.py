import psutil
from rpa_quaestvm.logger import Logger

logger = Logger.get_logger("logs/metrics.log", name="Metrics_Logger")

def create_sampler():
    """
    Retorna um sampler leve que captura cpu% (desde última chamada) e RSS em MB.
    Se psutil não estiver disponível, retorna sampler que devolve None.
    Uso: sampler = _create_sampler(); sampler() -> {"cpu_percent": float|None, "rss_mb": float|None}
    """
    try:
        proc = psutil.Process()
        proc.cpu_percent(interval=None)  # inicializa
    except Exception:
        proc = None

    def sampler():
        if proc is None:
            return {"cpu_percent": None, "rss_mb": None}
        try:
            return {
                "cpu_percent": proc.cpu_percent(interval=None),
                "rss_mb": proc.memory_info().rss / (1024.0 * 1024.0),
            }
        except Exception:
            return {"cpu_percent": None, "rss_mb": None}

    return sampler


def aggregate_samples(samples: list[dict]):
    """Retorna (avg_cpu, peak_rss) a partir da lista de amostras."""
    cpu_vals = [s["cpu_percent"] for s in samples if s.get("cpu_percent") is not None]
    rss_vals = [s["rss_mb"] for s in samples if s.get("rss_mb") is not None]
    avg_cpu = (sum(cpu_vals) / len(cpu_vals)) if cpu_vals else None
    peak_rss = max(rss_vals) if rss_vals else None
    return avg_cpu, peak_rss


def log_metrics(msg: str, duracao, samples):
    cpu_avg, rss_peak = aggregate_samples(samples)
    logger.info(
        f"{msg} - duração={duracao:.2f}s - "
        f"cpu_avg={cpu_avg if cpu_avg is None else f'{cpu_avg:.1f}%'} - "
        f"rss_peak={rss_peak if rss_peak is None else f'{rss_peak:.1f}MB'}"
    )
