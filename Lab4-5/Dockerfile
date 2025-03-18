FROM node:23-bookworm AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:23-bookworm AS deploy
ENV PYTHONIOENCODING=utf-8
RUN apt-get update && apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get clean -y && apt-get autoclean -y

RUN pip3 install "fastapi[standard]" --break-system-packages
COPY --from=build /app/requirements.txt ./
#RUN pip3 install --break-system-packages -r requirements.txt

WORKDIR /app
COPY --from=build /app/package.json ./
COPY --from=build /app/package-lock.json ./
RUN npm ci --only=production

COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/API ./
COPY --from=build /app/run.sh ./

EXPOSE 3000

RUN chmod +x run.sh
CMD ["./run.sh"]
