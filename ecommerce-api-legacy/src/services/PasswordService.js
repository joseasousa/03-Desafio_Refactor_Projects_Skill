const crypto = require('crypto');

class PasswordService {
    hash(password) {
        const salt = crypto.randomBytes(16).toString('hex');
        const hash = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256').toString('hex');
        return `pbkdf2_sha256$${salt}$${hash}`;
    }
}

module.exports = PasswordService;
