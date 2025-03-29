FROM node:23-bookworm AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install
ENV NEXT_TELEMETRY_DISABLED=1
COPY . .
RUN npm run build

FROM node:23-bookworm AS deploy

ENV PYTHONIOENCODING=utf-8
ENV NEXT_TELEMETRY_DISABLED=1

# Install Python, nginx, and required packages
RUN apt-get update && apt-get install -y python3 python3-pip nginx && \
    apt-get clean -y && apt-get autoclean -y

RUN pip3 install "fastapi[standard]" --break-system-packages
COPY --from=build /app/requirements.txt ./
# RUN pip3 install --break-system-packages -r requirements.txt

WORKDIR /app
COPY --from=build /app/package.json ./
COPY --from=build /app/package-lock.json ./
RUN npm ci --only=production

COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/API ./API
COPY --from=build /app/run.sh ./

# Copy our nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 3000
EXPOSE 8000

RUN chmod +x run.sh 
CMD ["./run.sh"]