const config = {
    port: Number(process.env.PORT || 3000),
    adminToken: process.env.ADMIN_TOKEN || null
};

module.exports = config;
