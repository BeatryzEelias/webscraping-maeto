from bs4 import BeautifulSoup
import sqlite3
import re
import requests

banco = sqlite3.connect('banco.db')
cursor = banco.cursor()

nome_prod = input("Digite o nome do Produto:")
url = f"https://www.lojamaeto.com/search/?q={nome_prod}"
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')

produtos = soup.find_all('div', class_ ='product')

print(f"Produto encontrado: {len(produtos)}")

for prod in produtos:

    titulo_tag = prod.find("h4", class_='product-list-name')
    link_tag = titulo_tag.find('a') if titulo_tag else None
    titulo = link_tag.text.strip()
    link =  f"https://www.lojamaeto.com{link_tag['href']}" if link_tag else "Link não encontrado"

    sku = prod.find('div',class_='sku-active')
    sku = sku.text.strip() if sku else "SKU não encontrado"

    preco = prod.find('div', class_='price')
    preco_text = preco.text.strip() if preco else "Preço não encontrado"

    preco_pix = prod.find('span', id='pixChangePrice')

    preco = "Preço não encontrado"
    num_parcelas = "Não disponível"
    valor_parcela = "Não disponível"
    info_tecnicas = "Não disponível"

    if link:
        detalhe_html = requests.get(link).text
        detalhe_soup = BeautifulSoup(detalhe_html,'html.parser')
        desc= (
        detalhe_soup.find('div',id='product-information')
       
)
    
    if desc:
            info_tecnicas = desc.get_text(strip=True)
    else:
            info_tecnicas = "Descrição tecnica não encontrada"

    if "R$" in preco_text:
        partes = preco_text.split("R$")
        if len(partes) > 1:
            preco = "R$" + partes[1].split()[0]

    if "pix" in preco_text.lower():
        pix_pix = preco_text.lower().find("pix")
        preco_pix = preco_text[max(0,pix_pix-10):pix_pix].strip()
    
        match = re.search(r"(\d+)\s*x\s*de\s*R\$\s*([\d.,]+)", preco_text)
        if match:
            num_parcelas = match.group(1)
            valor_parcela = f"R${match.group(2)}"
        else:
            num_parcelas = "Não Disponível"
            valor_parcela = "Não Disponível"

    print(f"Título: {titulo}")
    print(f"Link: {link}")
    print(f"SKU: {sku}")
    print(f"Preço: {preco}")
    print(f"Preço no Pix: {preco_pix}")
    print(f"Parcelas: {num_parcelas}")
    print(f"Valor das Parcelas: {valor_parcela}")
    print(f"Informações tecnicas: {info_tecnicas}")
    print("-" * 40)


    cursor.execute("SELECT * FROM produtos WHERE sku = ?", (sku,))
existe = cursor.fetchall()

if existe:
    cursor.execute("""
        UPDATE produtos 
        SET titulo = ?, link = ?, preco = ?, preco_pix = ?, valor_parcela = ?, num_parcelas = ?, info_tecnicas = ?
        WHERE sku = ?
    """, (titulo, link, preco, preco_pix, valor_parcela, num_parcelas, info_tecnicas,sku))
    print("Atualização no Banco de dados criada com sucesso.")
else:
    cursor.execute("""
        INSERT INTO produtos (sku, titulo, link, preco, preco_pix, valor_parcela, num_parcelas, info_tecnicas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (sku, titulo, link, preco, preco_pix, valor_parcela, num_parcelas, info_tecnicas))
    print("Inserido no Banco de dados com sucesso.")

banco.commit()
banco.close()
