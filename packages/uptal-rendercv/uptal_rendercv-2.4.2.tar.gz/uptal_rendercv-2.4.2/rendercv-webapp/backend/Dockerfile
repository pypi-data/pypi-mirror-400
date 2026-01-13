FROM python:3.13-slim

WORKDIR /app

# Install Typst for PDF generation
RUN apt-get update && apt-get install -y wget xz-utils && \
    wget https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz && \
    tar -xf typst-x86_64-unknown-linux-musl.tar.xz && \
    mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/ && \
    chmod +x /usr/local/bin/typst && \
    rm -rf typst-x86_64-unknown-linux-musl* && \
    apt-get remove -y wget xz-utils && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p generated_pdfs

EXPOSE 5000

CMD ["python", "app.py"]