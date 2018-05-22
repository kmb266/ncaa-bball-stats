const ElectronOnline = require('electron-online')
const connection = new ElectronOnline()

connection.on('online', () => {
  console.log('App is online!')
  require('./update_dbs');
})

connection.on('offline', () => {
  console.log('App is offline!')
})

console.log(connection.status) // 'PENDING'
