from PySide6.QtWidgets import QProxyStyle, QStyle


class LineIconsProxyStyle(QProxyStyle):

    def pixelMetric(self, metric, option=None, widget=None):
        if metric == QStyle.PM_SmallIconSize:
            return 100
        else:
            return super().pixelMetric(metric, option, widget)
