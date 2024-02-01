//$(document).ready(function() {

    //  -- Зміна сторінок в Пагінаторі
    function SelectPage(element, cur_page) {
        let table = $('#id_rep_table');                 //  Отримуємо посилання на таблицю звіту
        let headerRows = table.find('tr:has(th)');      //  Вибираємо всі рядки таблиці, які містять елементи <th>
        let th_count = headerRows.length;               //  кількість рядків у заголовку таблиці
        th_count += btn_add_global;                     //  + рядок з кнопкою додавання запису, якщо є
        let rows = table.find('tr');                    // Отримуємо всі рядки таблиці
        let total_row = rows.length - th_count;         //  кількість рядків звіту без заголовку
        let limit = parseInt( $('#id_limit').val() );   //  кількість на сторінці беремо зі сторінки
        let total_pages = Math.ceil( total_row/limit);  //  кількість сторінок

        //  вираховуємо сторінку, на яку потрібно перейти
        if (element) {
            let selector = $(element).text()
            switch (selector) {
                case '«':
                    page = 1
                    break;
                case '»':
                    page = total_pages
                    break;
                case '›':
                    page = cur_page + 1
                    break;
                case '‹':
                    page = cur_page - 1
                    break;
                default:
                    page = parseInt(selector);
            }
        } else {
            page = cur_page;
        }

        //  при зміні limit
        if ( page > total_pages ) page = total_pages;
        // останній порядковий номер номер запису сторінки <page>
        let last_row = page * limit + th_count - 1;
        // перший порядковий номер номер запису сторінки <page>
        let first_row = last_row - limit + 1 ;
           // console.log('first_row=',first_row, 'last_row=',last_row, 'th_count=', th_count)

        //  проходимо по всіх рядках за виключенням заголовка та рядка з кнопкою додавання запису
        for (var i = th_count; i < rows.length; i++) {
            //  показуємо рядок
            if (i >= first_row && i <= last_row) {
                //rows[i].style.display = 'table-row';
                $(rows[i]).show();
            }
            else {  //  ховаємо рядок
                // rows[i].style.display = 'none';
                $(rows[i]).hide();
            }
        }
        //  формуємо новий пагінатор
        paginator(page, limit, total_pages, total_row);
    }

    //  -- Додавання пагінатора на сторінку
    function paginator(page, limit, total_pages, total_row) {
        // ----- Видалення всіх елементів <li>
        $('#id_ul_pages').empty();
        let newLi1;
        let newLi2;
        // ----- Створення нових елементів <li>
        // Додаємо  '<<' та '<'
        if ( page == 1 ) {   //  перша сторінка
            $('#id_ul_pages').append( $('<li class="page-item disabled"><a class="page-link">«</a></li>') );
            $('#id_ul_pages').append( $('<li class="page-item disabled"><a class="page-link">‹</a></li>') );
        }
        else {
            // Створення нового елемента li з внутрішнім a і додавання обробника подій
            newLi1 = $('<li class="page-item"><a class="page-link">«</a></li>').click(function() {
                SelectPage(this, page);
            });
            newLi2 = $('<li class="page-item"><a class="page-link">‹</a></li>').click(function() {
                SelectPage(this, page);
            });
            // Додавання нового li до ul
            $('#id_ul_pages').append(newLi1, newLi2);
        }

        //  додаємо сторінки
        for (let i = 1; i <= total_pages; i++) {
            if ( i == page ) {   //  поточна сторінка
                newLi1 = $('<li class="page-item active"><a class="page-link">'+ i +'</a></li>').click(function() {
                    SelectPage(this, i);
                });
            }
            else {
                newLi1 = $('<li class="page-item"><a class="page-link">'+ i +'</a></li>').click(function() {
                    SelectPage(this, i);
                });
            }
            $('#id_ul_pages').append(newLi1);
        }

        // Додаємо  '<' та '<<'
        if ( page == total_pages ) {   //  остання сторінка
            $('#id_ul_pages').append( $('<li class="page-item disabled"><a class="page-link">›</a></li>') );
            $('#id_ul_pages').append( $('<li class="page-item disabled"><a class="page-link">»</a></li>') );
        }
        else {
            newLi1 = $('<li class="page-item"><a class="page-link">›</a></li>').click(function() {
                SelectPage(this, page);
            });
            newLi2 = $('<li class="page-item"><a class="page-link">»</a></li>').click(function() {
                SelectPage(this, page);
            });
            $('#id_ul_pages').append(newLi1, newLi2);
        }
        //  змінюємо глобальні параметри
        page_global = page
        limit_global = limit
    }

    //  запускаємо перший раз при виводі сторінки
    //if (typeof page_global == 'undefined' ) { page_global = 1; }
    //SelectPage(undefined, page_global);
//});
