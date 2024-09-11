# Apex Legends Player Monitor

## Apex API Portal

[Home](https://portal.apexlegendsapi.com/)

## API Reference

[Documentation](https://apexlegendsapi.com/)

考慮玩家名稱可能會有重複或是會更改，因此使用 ID 來做為唯一識別碼，可利用以下第一支 API 來取得 ID

### Query by name

**HTTP Request**  
`GET https://api.mozambiquehe.re/bridge?auth=YOUR_API_KEY&player=PLAYER_NAME&platform=PLATFORM`

### Query by UID

**HTTP Request**  
`GET https://api.mozambiquehe.re/bridge?auth=YOUR_API_KEY&uid=PLAYER_UID&platform=PLATFORM`
