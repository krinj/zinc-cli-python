import ZincContentInterface from "./zincContentInterface";

class ZincContent extends ZincContentInterface {
    constructor () {
        super();
        this.addBody('This is injected content!');
        this.addBody('This is injected content!');
        this.addBody('This is injected content!');
    }
}

export default ZincContent

