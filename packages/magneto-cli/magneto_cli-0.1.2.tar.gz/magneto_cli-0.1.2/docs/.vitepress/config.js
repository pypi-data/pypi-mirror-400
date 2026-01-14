import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Magneto',
  description: 'A powerful command-line tool for batch converting torrent files to magnet links',
  
  // GitHub Pages base path
  base: '/magneto/',
  
  // 默认语言
  defaultLocale: 'en',
  
  // 移除 URL 中的 .html 后缀
  cleanUrls: true,
  
  // 图标配置 - 使用绝对路径
  head: [
    ['link', { rel: 'favicon', href: '/favicon.ico', type: 'image/x-icon' }],
  ],
  
  
  // 多语言配置
  locales: {
    root: {
      label: 'English',
      lang: 'en',
      title: 'Magneto',
      description: 'A powerful command-line tool for batch converting torrent files to magnet links',
      themeConfig: {
        logo: '/icon.svg',
        nav: [
          { text: 'Introduction', link: '/introduction' },
          { text: 'Getting Started', link: '/getting-started' },
          { text: 'Installation', link: '/installation' },
          { text: 'Usage', link: '/usage' },
          { text: 'API Reference', link: '/api-reference' }
        ],
        sidebar: {
          '/': [
            {
              text: 'Guide',
              items: [
                { text: 'Introduction', link: '/introduction' },
                { text: 'Getting Started', link: '/getting-started' },
                { text: 'Installation', link: '/installation' },
                { text: 'Usage', link: '/usage' }
              ]
            },
            {
              text: 'Reference',
              items: [
                { text: 'API Reference', link: '/api-reference' }
              ]
            }
          ]
        },
        // 搜索配置
        search: {
          provider: 'local'
        },
        // 社交链接
        socialLinks: [
          { icon: 'github', link: 'https://github.com/mastaBriX/magneto' }
        ],
        // 页脚
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 Magneto Contributors'
        },
        // 编辑链接
        editLink: {
          pattern: 'https://github.com/mastaBriX/magneto/edit/main/docs/:path',
          text: 'Edit this page on GitHub'
        }
      }
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      title: 'Magneto',
      description: '强大的命令行工具，用于批量将种子文件转换为磁力链接',
      themeConfig: {
        logo: '/icon.svg',
        nav: [
          { text: '介绍', link: '/zh/introduction' },
          { text: '快速开始', link: '/zh/getting-started' },
          { text: '安装', link: '/zh/installation' },
          { text: '使用指南', link: '/zh/usage' },
          { text: 'API 参考', link: '/zh/api-reference' }
        ],
        sidebar: {
          '/zh/': [
            {
              text: '指南',
              items: [
                { text: '介绍', link: '/zh/introduction' },
                { text: '快速开始', link: '/zh/getting-started' },
                { text: '安装', link: '/zh/installation' },
                { text: '使用指南', link: '/zh/usage' }
              ]
            },
            {
              text: '参考',
              items: [
                { text: 'API 参考', link: '/zh/api-reference' }
              ]
            }
          ]
        },
        search: {
          provider: 'local'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/mastaBriX/magneto' }
        ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 Magneto Contributors'
        },
        editLink: {
          pattern: 'https://github.com/mastaBriX/magneto/edit/main/docs/:path',
          text: '在 GitHub 上编辑此页'
        }
      }
    },
    'zh-TW': {
      label: '繁體中文',
      lang: 'zh-TW',
      title: 'Magneto',
      description: '強大的命令列工具，用於批次將種子檔案轉換為磁力連結',
      themeConfig: {
        logo: '/icon.svg',
        nav: [
          { text: '介紹', link: '/zh-TW/introduction' },
          { text: '快速開始', link: '/zh-TW/getting-started' },
          { text: '安裝', link: '/zh-TW/installation' },
          { text: '使用指南', link: '/zh-TW/usage' },
          { text: 'API 參考', link: '/zh-TW/api-reference' }
        ],
        sidebar: {
          '/zh-TW/': [
            {
              text: '指南',
              items: [
                { text: '介紹', link: '/zh-TW/introduction' },
                { text: '快速開始', link: '/zh-TW/getting-started' },
                { text: '安裝', link: '/zh-TW/installation' },
                { text: '使用指南', link: '/zh-TW/usage' }
              ]
            },
            {
              text: '參考',
              items: [
                { text: 'API 參考', link: '/zh-TW/api-reference' }
              ]
            }
          ]
        },
        search: {
          provider: 'local'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/mastaBriX/magneto' }
        ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 Magneto Contributors'
        },
        editLink: {
          pattern: 'https://github.com/mastaBriX/magneto/edit/main/docs/:path',
          text: '在 GitHub 上編輯此頁'
        }
      }
    },
    ja: {
      label: '日本語',
      lang: 'ja',
      title: 'Magneto',
      description: 'トーrentファイルをマグネットリンクに一括変換する強力なコマンドラインツール',
      themeConfig: {
        logo: '/icon.svg',
        nav: [
          { text: '紹介', link: '/ja/introduction' },
          { text: 'はじめに', link: '/ja/getting-started' },
          { text: 'インストール', link: '/ja/installation' },
          { text: '使用方法', link: '/ja/usage' },
          { text: 'API リファレンス', link: '/ja/api-reference' }
        ],
        sidebar: {
          '/ja/': [
            {
              text: 'ガイド',
              items: [
                { text: '紹介', link: '/ja/introduction' },
                { text: 'はじめに', link: '/ja/getting-started' },
                { text: 'インストール', link: '/ja/installation' },
                { text: '使用方法', link: '/ja/usage' }
              ]
            },
            {
              text: 'リファレンス',
              items: [
                { text: 'API リファレンス', link: '/ja/api-reference' }
              ]
            }
          ]
        },
        search: {
          provider: 'local'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/mastaBriX/magneto' }
        ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 Magneto Contributors'
        },
        editLink: {
          pattern: 'https://github.com/mastaBriX/magneto/edit/main/docs/:path',
          text: 'GitHub でこのページを編集'
        }
      }
    },
    ru: {
      label: 'Русский',
      lang: 'ru',
      title: 'Magneto',
      description: 'Мощный инструмент командной строки для пакетного преобразования торрент-файлов в магнитные ссылки',
      themeConfig: {
        logo: '/icon.svg',
        nav: [
          { text: 'Введение', link: '/ru/introduction' },
          { text: 'Начало работы', link: '/ru/getting-started' },
          { text: 'Установка', link: '/ru/installation' },
          { text: 'Использование', link: '/ru/usage' },
          { text: 'Справочник API', link: '/ru/api-reference' }
        ],
        sidebar: {
          '/ru/': [
            {
              text: 'Руководство',
              items: [
                { text: 'Введение', link: '/ru/introduction' },
                { text: 'Начало работы', link: '/ru/getting-started' },
                { text: 'Установка', link: '/ru/installation' },
                { text: 'Использование', link: '/ru/usage' }
              ]
            },
            {
              text: 'Справочник',
              items: [
                { text: 'Справочник API', link: '/ru/api-reference' }
              ]
            }
          ]
        },
        search: {
          provider: 'local'
        },
        socialLinks: [
          { icon: 'github', link: 'https://github.com/mastaBriX/magneto' }
        ],
        footer: {
          message: 'Released under the MIT License.',
          copyright: 'Copyright © 2024 Magneto Contributors'
        },
        editLink: {
          pattern: 'https://github.com/mastaBriX/magneto/edit/main/docs/:path',
          text: 'Редактировать эту страницу на GitHub'
        }
      }
    }
  }
})

