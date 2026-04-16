class FinancialReportService {
    constructor(reportRepository) {
        this.reportRepository = reportRepository;
    }

    async buildReport() {
        const rows = await this.reportRepository.fetchRows();
        const reportByCourse = new Map();

        for (const row of rows) {
            if (!reportByCourse.has(row.course_id)) {
                reportByCourse.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }

            const courseData = reportByCourse.get(row.course_id);

            if (!row.student_name) {
                continue;
            }

            if (row.payment_status === 'PAID') {
                courseData.revenue += row.payment_amount;
            }

            courseData.students.push({
                student: row.student_name,
                paid: row.payment_amount || 0
            });
        }

        return Array.from(reportByCourse.values());
    }
}

module.exports = FinancialReportService;
