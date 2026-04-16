class CheckoutService {
    constructor({ users, courses, enrollments, payments, auditLogs, passwordService, paymentService }) {
        this.users = users;
        this.courses = courses;
        this.enrollments = enrollments;
        this.payments = payments;
        this.auditLogs = auditLogs;
        this.passwordService = passwordService;
        this.paymentService = paymentService;
    }

    async checkout({ userName, email, password, courseId, cardNumber }) {
        const course = await this.courses.findActiveById(courseId);

        if (!course) {
            return { status: 'COURSE_NOT_FOUND' };
        }

        const existingUser = await this.users.findByEmail(email);
        const userId = existingUser ? existingUser.id : await this.createUser(userName, email, password);
        const paymentStatus = this.paymentService.charge(cardNumber);

        if (paymentStatus === 'DENIED') {
            return { status: 'PAYMENT_DENIED' };
        }

        const enrollment = await this.enrollments.create({ userId, courseId });

        await this.payments.create({
            enrollmentId: enrollment.lastID,
            amount: course.price,
            status: paymentStatus
        });
        await this.auditLogs.create(`Checkout curso ${courseId} por ${userId}`);

        return {
            status: 'SUCCESS',
            enrollmentId: enrollment.lastID
        };
    }

    async createUser(name, email, password) {
        const result = await this.users.create({
            name,
            email,
            passwordHash: this.passwordService.hash(password)
        });

        return result.lastID;
    }
}

module.exports = CheckoutService;
