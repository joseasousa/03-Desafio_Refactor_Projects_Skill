const express = require('express');

const config = require('./config');
const database = require('./database');
const registerRoutes = require('./routes');
const createAdminAuth = require('./middleware/adminAuth');

const AuditLogRepository = require('./models/AuditLogRepository');
const CourseRepository = require('./models/CourseRepository');
const EnrollmentRepository = require('./models/EnrollmentRepository');
const FinancialReportRepository = require('./models/FinancialReportRepository');
const PaymentRepository = require('./models/PaymentRepository');
const UserRepository = require('./models/UserRepository');

const CheckoutController = require('./controllers/CheckoutController');
const FinancialReportController = require('./controllers/FinancialReportController');
const UserController = require('./controllers/UserController');

const CheckoutService = require('./services/CheckoutService');
const FinancialReportService = require('./services/FinancialReportService');
const PasswordService = require('./services/PasswordService');
const PaymentService = require('./services/PaymentService');
const UserService = require('./services/UserService');

async function createApp() {
    const app = express();
    const db = database.createDatabase();
    const passwordService = new PasswordService();

    await database.initializeDatabase(db, passwordService);

    const databaseAdapter = {
        all: (sql, params) => database.all(db, sql, params),
        get: (sql, params) => database.get(db, sql, params),
        run: (sql, params) => database.run(db, sql, params)
    };

    const users = new UserRepository(databaseAdapter);
    const checkoutService = new CheckoutService({
        users,
        courses: new CourseRepository(databaseAdapter),
        enrollments: new EnrollmentRepository(databaseAdapter),
        payments: new PaymentRepository(databaseAdapter),
        auditLogs: new AuditLogRepository(databaseAdapter),
        passwordService,
        paymentService: new PaymentService()
    });
    const reportService = new FinancialReportService(new FinancialReportRepository(databaseAdapter));
    const userService = new UserService(users);

    app.use(express.json());
    registerRoutes(app, {
        checkoutController: new CheckoutController(checkoutService),
        financialReportController: new FinancialReportController(reportService),
        userController: new UserController(userService),
        adminAuth: createAdminAuth(config.adminToken)
    });

    app.locals.db = db;
    return app;
}

async function start() {
    const app = await createApp();

    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

if (require.main === module) {
    start().catch((err) => {
        console.error(err);
        process.exit(1);
    });
}

module.exports = { createApp, start };
