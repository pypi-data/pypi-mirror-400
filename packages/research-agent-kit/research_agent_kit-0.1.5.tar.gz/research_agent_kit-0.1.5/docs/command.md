# Deploy

## Build
docker build -t research-api .

## Test
docker run --rm -p 8999:8000 research-api

## Production environment
docker run -d --rm -p 8003:8000 research-api


# How to get openapi.json
curl -o openapi.json http://localhost:8000/openapi.json
jq . docs/openapi.json > /tmp/openapi.json && mv /tmp/openapi.json docs/openapi.json

# Test
curl -i \
  -H "X-API-Key: 7AeqtgTwHMF92amX74qZtc9D3lyte0yR" \
  https://keisukes-macbook-pro.tail6acff1.ts.net/research

curl -X POST "https://keisukes-macbook-pro.tail6acff1.ts.net/research/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 7AeqtgTwHMF92amX74qZtc9D3lyte0yR" \
  --max-time 600 \
  -d '{"topic":"hello, how are you"}'
