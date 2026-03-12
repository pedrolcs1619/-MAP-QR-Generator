//explaning variable
interface Item {
    nome: string;
    quantidade: number;
    preco: number;
    taxa: boolean;
}



interface Cliente {
    nome: string;
    email: string;
    vip: boolean;
    endereco: string;
}



class CalculoFatura {}



// Single Responsibility Principle

class InvoiceGen {
    private data: Item[] = [];
    private cliente: Cliente;


    constructor(cliente: Cliente) { this.cliente = cliente; }


    add(item: Item): void { this.data.push(item); }


    verifica_existencia_itens() {
        if (this.data.length === 0) {

            throw new Error('sem itens');

        }
        return true;
    }

    validaco_email() {
        if (!this.cliente.email.includes('@')) {

            throw new Error('email inv');

        }
    }

    calculo_subtotal(): number {
        return this.data.reduce((acc, item) => {
            const valorBase = item.quantidade * item.preco;
            return acc + (item.taxa ? valorBase * 1.12 : valorBase);
        }, 0);
    }

    verifica_cliente_vip(numero: number): number {
        return this.cliente.vip ? numero * 0.9 : numero;
    }




    //criar classe para isso
    //v 

    gerarCaecalho(): string {
        return `FATURA\n` +
            `Cliente: ${this.cliente.nome}\n` +
            `Endereço: ${this.cliente.endereco}\n` +
            `Email: ${this.cliente.email}\n\n`;
    }

    gerarLinhasItens(): string {
        let linhas = `ITENS:\n`;
        for (const item of this.data) {
            linhas += `  ${item.nome.padEnd(15)} x${item.quantidade} @ R$${item.preco.toFixed(2).padStart(8)}\n`;
        }
        return linhas;
    }

    gerarRodape(sub: number, taxa: number, desconto: number, total: number): string {
        return `\n` +
            `Subtotal:  R$${sub.toFixed(2).padStart(8)}\n` +
            `Impostos:  R$${taxa.toFixed(2).padStart(8)}\n` +
            `Desconto: -R$${desconto.toFixed(2).padStart(8)}\n` +
            `---------------------------\n` +
            `TOTAL:     R$${total.toFixed(2).padStart(8)}\n`;
    }







    Main(): string {


        this.verifica_existencia_itens();
        this.validaco_email();

        const sub = this.calculo_subtotal();

        const disc = this.verifica_cliente_vip(sub);
        const taxa = sub - disc;
        const total = disc + taxa;
        const cabecalho = this.gerarCaecalho();
        const linhas = this.gerarLinhasItens();
        const rodape = this.gerarRodape(sub, taxa, disc, total);
        return cabecalho + linhas + rodape;


    }
}


const clienteExemplo = {
    nome: "João Silva",
    email: "joao@email.com",
    vip: true,
    endereco: "Rua das Flores, 123"
};

const fatura = new InvoiceGen(clienteExemplo);

fatura.add({ nome: "Teclado Mecânico", quantidade: 1, preco: 150.00, taxa: true });
fatura.add({ nome: "Mouse Gamer", quantidade: 1, preco: 80.00, taxa: false });

console.log(fatura.Main());