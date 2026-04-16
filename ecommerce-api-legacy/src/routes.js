function registerRoutes(app, { checkoutController, financialReportController, userController, adminAuth }) {
    app.post('/api/checkout', checkoutController.create);
    app.get('/api/admin/financial-report', adminAuth, financialReportController.show);
    app.delete('/api/users/:id', userController.destroy);
}

module.exports = registerRoutes;
