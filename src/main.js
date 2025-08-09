const { app, BrowserWindow, ipcMain, session, dialog, Menu } = require('electron');
const path = require('path');
const PrivacyEngine = require('./privacy/privacyEngine');
const NetworkProtection = require('./network/networkProtection');
const FingerprintProtection = require('./fingerprint/fingerprintProtection');
const SecurityManager = require('./security/securityManager');

class AnDetectBrowser {
    constructor() {
        this.mainWindow = null;
        this.privacyEngine = new PrivacyEngine();
        this.networkProtection = new NetworkProtection();
        this.fingerprintProtection = new FingerprintProtection();
        this.securityManager = new SecurityManager();
        this.isDevMode = process.argv.includes('--dev');
        
        this.initializeApp();
    }

    initializeApp() {
        app.whenReady().then(() => {
            this.createMainWindow();
            this.setupEventHandlers();
            this.initializeProtections();
            
            // Додаткова безпека: відключення небезпечних функцій
            app.on('web-contents-created', (event, contents) => {
                this.secureWebContents(contents);
            });
        });

        app.on('window-all-closed', () => {
            this.cleanup();
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                this.createMainWindow();
            }
        });
    }

    createMainWindow() {
        // Створення основного вікна з налаштуваннями безпеки
        this.mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            minWidth: 800,
            minHeight: 600,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                webSecurity: true,
                allowRunningInsecureContent: false,
                experimentalFeatures: false,
                preload: path.join(__dirname, 'preload.js')
            },
            icon: path.join(__dirname, '../assets/icon.png'),
            show: false,
            titleBarStyle: 'hiddenInset'
        });

        // Завантаження головної сторінки
        this.mainWindow.loadFile(path.join(__dirname, 'ui/index.html'));

        // Показати вікно після завантаження
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            if (this.isDevMode) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        // Обробка закриття вікна
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
            this.cleanup();
        });

        // Створення меню
        this.createApplicationMenu();
    }

    secureWebContents(contents) {
        // Блокування небезпечних дій
        contents.on('will-navigate', (event, navigationUrl) => {
            if (!this.securityManager.isUrlSafe(navigationUrl)) {
                event.preventDefault();
                this.showSecurityWarning('Заблоковано підозрілий URL');
            }
        });

        contents.on('new-window', (event, windowUrl) => {
            event.preventDefault();
            // Відкриваємо в тому ж вікні з захистом
            this.navigateSecurely(windowUrl);
        });

        // Відключення небезпечних API
        contents.on('will-attach-webview', (event) => {
            event.preventDefault();
        });
    }

    async initializeProtections() {
        try {
            await this.privacyEngine.initialize();
            await this.networkProtection.initialize();
            await this.fingerprintProtection.initialize();
            await this.securityManager.initialize();
            
            console.log('Всі системи захисту ініціалізовані');
        } catch (error) {
            console.error('Помилка ініціалізації захисту:', error);
        }
    }

    setupEventHandlers() {
        // Навігація з захистом
        ipcMain.handle('navigate-to', async (event, url) => {
            return await this.navigateSecurely(url);
        });

        // Зміна налаштувань приватності
        ipcMain.handle('update-privacy-settings', async (event, settings) => {
            return await this.privacyEngine.updateSettings(settings);
        });

        // Керування VPN/Proxy
        ipcMain.handle('toggle-network-protection', async (event, enabled) => {
            return await this.networkProtection.toggle(enabled);
        });

        // Очищення даних
        ipcMain.handle('clear-browsing-data', async (event, options) => {
            return await this.clearBrowsingData(options);
        });

        // Отримання статусу захисту
        ipcMain.handle('get-protection-status', async () => {
            return {
                privacy: await this.privacyEngine.getStatus(),
                network: await this.networkProtection.getStatus(),
                fingerprint: await this.fingerprintProtection.getStatus(),
                security: await this.securityManager.getStatus()
            };
        });
    }

    async navigateSecurely(url) {
        try {
            // Перевірка безпеки URL
            if (!this.securityManager.isUrlSafe(url)) {
                throw new Error('URL заблоковано з міркувань безпеки');
            }

            // Застосування захисту від фінгерпрінтингу
            await this.fingerprintProtection.applyProtection();

            // Навігація
            await this.mainWindow.webContents.loadURL(url);
            
            return { success: true };
        } catch (error) {
            console.error('Помилка навігації:', error);
            return { success: false, error: error.message };
        }
    }

    async clearBrowsingData(options = {}) {
        const defaultOptions = {
            cache: true,
            cookies: true,
            localStorage: true,
            sessionStorage: true,
            indexedDB: true,
            webSQL: true,
            ...options
        };

        try {
            const ses = session.defaultSession;
            
            if (defaultOptions.cache) {
                await ses.clearCache();
            }
            
            if (defaultOptions.cookies) {
                await ses.clearStorageData({
                    storages: ['cookies']
                });
            }
            
            if (defaultOptions.localStorage || defaultOptions.sessionStorage) {
                await ses.clearStorageData({
                    storages: ['localstorage', 'sessionstorage']
                });
            }
            
            if (defaultOptions.indexedDB) {
                await ses.clearStorageData({
                    storages: ['indexdb']
                });
            }

            console.log('Дані браузера очищено');
            return { success: true };
        } catch (error) {
            console.error('Помилка очищення даних:', error);
            return { success: false, error: error.message };
        }
    }

    showSecurityWarning(message) {
        dialog.showMessageBox(this.mainWindow, {
            type: 'warning',
            title: 'Попередження безпеки',
            message: message,
            buttons: ['OK']
        });
    }

    createApplicationMenu() {
        const template = [
            {
                label: 'Файл',
                submenu: [
                    {
                        label: 'Нова вкладка',
                        accelerator: 'CmdOrCtrl+T',
                        click: () => {
                            // Функціонал нової вкладки
                        }
                    },
                    {
                        label: 'Приватне вікно',
                        accelerator: 'CmdOrCtrl+Shift+N',
                        click: () => {
                            // Відкриття приватного вікна
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Вихід',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'Захист',
                submenu: [
                    {
                        label: 'Очистити дані',
                        click: () => {
                            this.clearBrowsingData();
                        }
                    },
                    {
                        label: 'Налаштування приватності',
                        click: () => {
                            // Відкриття налаштувань
                        }
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    async cleanup() {
        try {
            // Автоматичне очищення при закритті
            await this.clearBrowsingData();
            
            // Очищення тимчасових файлів
            await this.privacyEngine.cleanup();
            
            console.log('Очищення завершено');
        } catch (error) {
            console.error('Помилка очищення:', error);
        }
    }
}

// Запуск браузера
new AnDetectBrowser();
