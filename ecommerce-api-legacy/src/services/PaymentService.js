class PaymentService {
    charge(cardNumber) {
        return cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
    }
}

module.exports = PaymentService;
