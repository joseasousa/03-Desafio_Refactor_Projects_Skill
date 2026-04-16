const validateCheckout = require('../validators/checkoutValidator');

class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
    }

    create = async (req, res) => {
        const validation = validateCheckout(req.body);

        if (validation.error) {
            res.status(400).send(validation.error);
            return;
        }

        try {
            const result = await this.checkoutService.checkout(validation.value);

            if (result.status === 'COURSE_NOT_FOUND') {
                res.status(404).send('Curso não encontrado');
                return;
            }

            if (result.status === 'PAYMENT_DENIED') {
                res.status(400).send('Pagamento recusado');
                return;
            }

            res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
        } catch (err) {
            res.status(500).send('Erro DB');
        }
    };
}

module.exports = CheckoutController;
