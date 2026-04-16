class FinancialReportController {
    constructor(reportService) {
        this.reportService = reportService;
    }

    show = async (req, res) => {
        try {
            const report = await this.reportService.buildReport();
            res.json(report);
        } catch (err) {
            res.status(500).send('Erro DB');
        }
    };
}

module.exports = FinancialReportController;
