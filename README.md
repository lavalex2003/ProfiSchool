<!DOCTYPE html>
<html>
<head>
    <title>ProfiMaktab Home Assistant Integration</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
        .code-block {
            background-color: var(--bs-dark);
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
</head>
<body data-bs-theme="dark">
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h1 class="card-title">ProfiMaktab Home Assistant Integration</h1>
                    </div>
                    <div class="card-body">
                        <h2>Интеграция Home Assistant для ProfiMaktab.uz</h2>
                        
                        <p class="mt-4">
                            Данная интеграция позволяет получать информацию об успеваемости учеников из системы ProfiMaktab 
                            и отображать её в вашей системе Home Assistant.
                        </p>

                        <h3 class="mt-4">Установка</h3>
                        <p>
                            Для установки интеграции вам необходимо скопировать папку <code>custom_components/profimaktab</code> 
                            в директорию <code>custom_components</code> вашего Home Assistant.
                        </p>

                        <div class="code-block">
# Установка через HACS (рекомендуется)
1. Перейдите в HACS на вашем Home Assistant
2. Выберите "Интеграции" 
3. Нажмите кнопку "+" в правом верхнем углу
4. Введите URL репозитория: https://github.com/lavalex2003/ProfiSchool
5. Нажмите "Установить"

# Ручная установка
1. Скопируйте папку custom_components/profimaktab в директорию custom_components вашего Home Assistant
2. Перезапустите Home Assistant
                        </div>

                        <h3 class="mt-4">Настройка</h3>
                        <p>
                            После установки интеграции:
                        </p>
                        <ol>
                            <li>Перейдите в раздел <b>Настройки</b> → <b>Интеграции</b></li>
                            <li>Нажмите на кнопку <b>+ Добавить интеграцию</b></li>
                            <li>Найдите и выберите <b>ProfiMaktab</b></li>
                            <li>Введите ваш логин и пароль от системы ProfiMaktab</li>
                            <li>Введите ID учеников, которых вы хотите отслеживать (разделяя запятыми)</li>
                        </ol>
                        
                        <h4 class="mt-3">Как получить уникальный номер студента?</h4>
                        <ol>
                            <li>Откройте сайт электронного журнала ProfiMaktab и авторизуйтесь в нём</li>
                            <li>Откройте в браузере режим разработчика (F12 или Ctrl+Shift+I)</li>
                            <li>Перейдите на вкладку "Сеть" (Network)</li>
                            <li>Обновите страницу и проследите за запросами</li>
                            <li>Найдите запросы, содержащие параметр <code>&student=xxxx</code></li>
                            <li>Значение <code>xxxx</code> - это и есть уникальный номер студента, который нужно указать при настройке интеграции</li>
                        </ol>

                        <h3 class="mt-4">Возможности</h3>
                        <p>
                            После установки и настройки, интеграция создаст сенсоры для каждого ученика с информацией о:
                        </p>
                        <ul>
                            <li>Средней оценке за текущий день</li>
                            <li>Деталях каждого урока (название, тема, оценка, домашнее задание)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
