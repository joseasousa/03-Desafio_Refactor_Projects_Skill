function createAdminAuth(adminToken) {
    return function adminAuth(req, res, next) {
        if (!adminToken) {
            next();
            return;
        }

        if (req.get('x-admin-token') === adminToken) {
            next();
            return;
        }

        res.status(401).send('Unauthorized');
    };
}

module.exports = createAdminAuth;
