$(function () {
    Array.prototype.fakeFindIndex = function (cb, context) {
        var array = this;

        for (var i = 0; i < array.length; i++) {
            var element = array[i];
            if (cb.call(context, element, i, array)) {
                return i
            }
        }
        return -1
    };

    window.operateEvents= {
        'click .rowDel': function (e, value, row, index) {
          console.log(row)
          if(confirm('确定要删除热词?')){

            allTableData.splice(allTableData.fakeFindIndex(function (item) {
                return item.id === row.id;
            }), 1);

            var res = get_words_from_data(allTableData);
            sync_words(res,'del')
          }

        }
    };

    // 人名，地名，专有名词 数组
    var  addWordList = [
        [],
        [],
        []
    ];
    //是否保存
    var addWordSaveFlag =  true;
    //添加：加号点击
    var btnAddFlag = false;
    //是否点击保存
    var isSaveClick  = false;
       //table全部数据
    var allTableData = [];


    init();

    function init(){
        initTable("all");
    }

    function initTable(type) {
        //先销毁表格
        $("#hotwords_table").bootstrapTable('destroy');
        //初始化表格，动态从服务器加载数据

        $("#hotwords_table").bootstrapTable({
            method:'get',
            url:'/web/allhotwords',
            reorderableRows: true,
            striped: true,
            search: false,
            toolbar: '#toolbar',
            useRowAttrFunc: true,
            uniqueId: 'id',
            pagination: true,
            onLoadSuccess :function(res){
                console.log("res",res)

                var finallArr = [];

                if(res.error_code == 0){
                    var  oldlist= res.words;
                    var  list = [];
                    for(var i=0;i<oldlist.length;i++){
                        list.push({
                            id:i+1,
                            words:oldlist[i].words,
                            type:oldlist[i].type,
                        })
                    }
                    allTableData = list;
                    console.log("list--返回的数据添加id",list)


                    var data = [];
                    for(var i=0;i<list.length;i++){
                        if(type == "all"){
                            data.push({
                                id:list[i].id,
                                words:list[i].words,
                                type:list[i].type,
                            })


                        }else {
                            if(type == list[i].type){
                                data.push({
                                    id:list[i].id,
                                    words:list[i].words,
                                    type:list[i].type,
                                })
                            }
                        }
                    }

                     console.log("data--过滤下拉数据",data)


                    for(var i=0;i<data.length;i++){
                        finallArr.push({
                            index:i+1,
                            id:data[i].id,
                            words:data[i].words,
                            type:data[i].type,
                        })
                    }

                    console.log("finallArr--添加index",finallArr)




                }else{
                     finallArr = []
                     allTableData = [];

                }

                 $("#hotwords_table").bootstrapTable("load",finallArr)

            },
            columns:[
                {
                    field: 'index',
                    title: '编号',
                    width:150
                  },
                  {
                    checkbox: true,
                    width:50
                  },
                  {
                    field: 'words',
                    title: '热词',
                    width:300
                  },
                  {
                    field: 'type',
                    title: '热词类型',
                    width:300,
                    formatter: typeFormatter

                  },
                  {
                    field: 'button',
                    title: '操作',
                    width:150,
                    events: operateEvents,
                    formatter: operateFormatter
                  }
            ]
        })

    }



    function typeFormatter(value, row, index) {
      var text="";
        if(value == "0"){
            text="人名";
        }else if(value == "1"){
            text="地名";
        }else if(value == "2"){
            text="专用名词";
        }
        return text;
    };


    function operateFormatter(value, row, index) {
        return [
          '<button type="button" class="btn btn-primary  rowDel">删除</button>'
        ].join('');
    };



    //批量删除按钮
    $("#batch-delete-btn").on("click",function(){
        //选中要删除的数组
        var array = $('#hotwords_table').bootstrapTable('getSelections');
        //console.log("delete-arr",array)

        if(array.length == 0){
            alert("请选择要删除的热词");
            return;
        }
        if(confirm('确定要删除热词?')){
            for(var i=0;i<array.length;i++){
                allTableData.splice(allTableData.fakeFindIndex(function (item) {
                    return item.id === array[i].id;
                }), 1);
            }

            var res = get_words_from_data(allTableData);
            sync_words(res,'del')

        }




    })





    function get_words_from_data(rows) {
        var res = [];
        for (var i = 0; i < rows.length; i++) { //遍历表格的行

          res.push({
            type:rows[i].type,
            words:rows[i].words
          })
        }

        return res;
    }
    function check_every_row_str_length(arr) {
        for (var i = 0; i < arr.length; i++) {
          if (arr[i].words.length > 10) {
            alert("Error:存在某个热词字符数量大于10");
            return false;
          }
        }
        return true;
    }

    function check_max_num(arr) {
        var p_num = 0
        var a_num = 0
        var pn_num = 0
        for (var i = 0; i < arr.length; i++) {
         if (arr[i]["type"] == 0) {
            p_num = p_num + 1
         } else if (arr[i]["type"] == 1) {
            a_num = a_num + 1
         } else {
            pn_num = pn_num + 1
         }
        }
        console.log("p_num:"+ p_num + ", a_num:" + a_num + ",pn_num:" + pn_num)
         // 判断是否超过最大限制
        if (p_num > 128 || a_num > 128 || pn_num > 128) {
            alert('人名、地名和专有名词均不能超过128个')
            return false;
        }
        return true;
    }

    function check_special_char(arr) {
        var tr = /[^\u4E00-\u9FA5]/ig
        for (var i = 0; i < arr.length; i++) {
          if (tr.test(arr[i]["words"])) {
            alert("Error:热词中存在英文、数字或特殊字符！");
            return false;
          }
        }
        return true;
    }

    // 上传热词
    function sync_words(arr,type) {
        console.log("arr---",arr)
        if (!check_max_num(arr)) {
          return;
        }
        if (!check_every_row_str_length(arr)) {
          return;
        }
        if (!check_special_char(arr)) {
          return;
        }
        if(type == "add"){
            isSaveClick = true;
        }

        var data = { "words": arr, "unique_id": "test123", "type": 0 }

        $.ajaxSetup({ "xhrFields": true });
        $.ajax({
          url: "/web/hotwords",
          data: JSON.stringify(data),
          contentType: "application/json",
          type: "Post",
          traditional: true,
          success: function (j) {
            if (j['error_code'] == 0) {


              if(type == "add"){
                addWordSaveFlag = true;
                isSaveClick = false;

                $('.add_word_area').html('')
                addWordList = [
                    [],
                    [],
                    []
                 ];

              }

              $("#hot_words_type option:first").prop("selected", "selected");
              initTable("all")

              if (type == 'add') {
                alert("热词发布成功");
              } else if (type == 'del') {
                alert("热词删除成功");
              } else {
                alert("热词导入成功");
              }
            } else {
              if (type == 'add') {
                alert("热词发布失败");
              } else if (type == 'del') {
                alert("热词删除失败");
              } else {
                alert("热词导入失败");
              }
            }
          }
        });
     }

        //下拉选择搜索
        $('#hot_words_type').change(function(){
            var val=$(this).children('option:selected').val();//这就是selected的值
            initTable(val);
        })

       //点击新增
        $("#add-btn").on("click",function(){
            $(".filter-box").css("display","none");
            $(".table-content").css("display","none");
            $(".add_box").css("display","block");
            $('.btn-wrap span:first').click();
       });

       // 类型切换
        $('.btn-wrap span').on("click",function() {
            $('.btn-wrap span').removeClass('current')
            $(this).addClass('current');
            var index = $(this).index();
            $('.hotword-text-wrap .hotword-text').hide()
            $('.hotword-text-wrap .hotword-text:eq(' + index + ')').show()
            // console.log(index)
        })

        // 添加 ---start
        $('#addWordSave').on("click",function(e) {
            e.preventDefault();

            var  hotwordList = []
            var arr = addWordList;
            for (var i = 0; i < arr.length; i++) {
                for (var j = 0; j < arr[i].length; j++) {
                    var obj = {
                        type: i,
                        words: arr[i][j]
                    }
                    hotwordList.push(obj)
                }
            }

            if (!hotwordList.length) {
                //弹窗提示未解决
                alert("Error:请至少输入一个热词！")
                return
            }

            //console.log("hotwordList",hotwordList)


            var res = get_words_from_data(allTableData);
            //console.log("res",res)
            var list = res.concat(hotwordList);
            //console.log("list",list)
            if(isSaveClick){
                return;
            }
            if(!addWordSaveFlag ){
                sync_words(list,'add')
            }
        })

        $('.btn-add').on("click",function() {
            btnAddFlag = true;
            $(".hotword-text-wrap .add_word_text").keyup()
        })

        $(".hotword-text-wrap .add_word_text").keyup(function(event) {
            var str = $.trim($(this).val())
            var $this = $(this);
            var index = $this.parents('.hotword-text').index();
            fnClearTips(index)


            var flag = fnCheckAddWord(str, index)
            // enter键入  或  .btn-add点击
            if (event.keyCode === 13 && str.length > 0 && flag || btnAddFlag && str.length > 0 && flag) {

                addWordSaveFlag = false
                btnAddFlag = false//针对加号的点击
                addWordList[index].push(str)
                fnAddWordListDom(index)
                $this.val('')

            }
        })

        $('.add_word_area  ').on('click', '.add_word_single i',function() {
            var item = $(this).attr('data');
            const index = $(this).attr('type');
            fnDelItem(item, index)
        })

        $('#btnBack').on("click",function() {
            if (addWordSaveFlag) {
                fnShowTableList()
            } else {
                //未解决弹窗
                if(confirm("热词未保存是否退出?")){
                    fnShowTableList()
                }
            }
        });
        $('#cancelWordSave').on("click",function() {
            $('#btnBack').click()
        })
        function fnDelItem (item, index) {
            var arr = addWordList[index]

            for (var v in arr) {
                if (arr[v] == item) {
                    arr.splice(v, 1)
                }
            }

            fnAddWordListDom(index)

        }
        function fnAddWordListDom (index) {
            var arr = addWordList[index]

            var html = ''
            for (var i = 0; i < arr.length; i++) {
                html += '<div class="add_word_single">';
                html += '<span>'+arr[i]+'</span>'
                html += '<i data="'+arr[i]+'" type="'+index+'">×</i>';
                html += '</div>';
            }
            $('.hotword-text-wrap .add_word_area:eq(' + index + ')').html(html)
        }

        function  fnClearTips (index) {
            var tips = $('.addWordTips');
            if(index){
                tips=$('.addWordTips').eq(index)
            }
            var str = "*每个热词不超过10个字符，格式仅支持中文 "
            tips.text(str).removeClass('red')
        }

         function  fnShowTableList () {
            // 添加初始化
            fnClearTips()
            addWordSaveFlag = true;
            isSaveClick = false;
            $('.add_word_area').html('')

            addWordList = [
                [],
                [],
                []
            ]

            $('.addWordText').val('')

            $(".filter-box").css("display","block")
            $(".table-content").css("display","block")
            $(".add_box").css("display","none")
//             var hot_words_type = $("#hot_words_type option:selected").val();
//            initTable(hot_words_type);
             $("#hot_words_type option:first").prop("selected", "selected");
             initTable("all")

        }


        function  fnCheckAddWord (str, index) {
            var tips = $('.addWordTips').eq(index);
            var reg = /[^\u4E00-\u9FA5]/ig
            var err = ''
            var arr = addWordList  && addWordList[index]  || [];
            // console.log(arr)
            if (str === null || str === "") {
                tips.addClass("red").text("请填写热词！");
                return false;
            }

            if (reg.test(str)) {
                err = '*热词格式仅支持中文'
                tips.text(err).addClass('red');
                return false
            }
            if (str.length > 10) {
                err = '热词长度超过10个字符'
                tips.text(err).addClass('red');
                return false
            }
            if(arr.length > 0){
                const isExit= arr.indexOf(str);
                if(isExit>=0){
                    err = '*热词重复添加'
                    tips.text(err).addClass('red');
                    return false
                }
            }

            if (err.length > 0) {
                tips.text(err).addClass('red')
                return false
            }
            return true
        }


        $('#export_hotwords_template').on("click",function() {
            var element = document.createElement('a');
            element.href = "/download/热词模板.xls";
            element.target = "_blank";
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
            setTimeout(function () {
              exportDialog.close();
            }, 2000);
        })

        $('#export_hotwords_excel').on("click",function() {
            // 下载热词excel文件
            var downurl = "/down_hot_words_excel"
            var element = document.createElement('a');
            element.href = downurl;
            element.target = "_blank";
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
            setTimeout(function () {
              exportDialog.close();
            }, 2000);
        })

        $('#import_hotwords_excel').on("change",function(e) {
            const file_list = event.target.files;
            console.log(file_list);
            // 读取excel文件
            var fileReader = new FileReader()
            fileReader.onload = function(ev) {
                try {
                    var data = ev.target.result
                    var workbook = XLSX.read(data, {
                        type: 'binary'
                    })

                    // 存储获取到的数据
                    var hotwordList = get_words_from_data(allTableData);

                    // 第一页
                    var sheet0 = workbook.Sheets[workbook.SheetNames[0]]
                    var rows = XLSX.utils.sheet_to_json(sheet0)
                    for (var i = 0; i < rows.length; i++) {
                      var type = 2
                      if (rows[i]["类型"] == '人名') {
                        type = 0
                      } else if (rows[i]["类型"] == '地名') {
                        type = 1
                      }

                      var obj = {
                         type: type,
                         words: rows[i]['热词']
                      }
                      hotwordList.push(obj)
                    }
                    sync_words(hotwordList, 'import')
                    document.getElementById('import_hotwords_excel').value = null;
                } catch (e) {
                    alert('Error:请选择正确的文件')
                    document.getElementById('import_hotwords_excel').value = null;
                    return
                }
          }

          var suffix = file_list[0].name.split(".")[1]
          if (suffix != 'xls' && suffix != 'xlsx') {
              alert('Error:请选择正确的文件')
              return;
          }

          // 以二进制方式打开文件
          fileReader.readAsBinaryString(file_list[0]);
        })
});





/*
  // DropzoneJS
  $(document).ready(function() {
    // 根据热词类型，获取相应的热词并显示在前端
    hot_words_type = $("#hot_words_type option:selected").val();
    $.ajaxSetup({ "xhrFields": true });
    $.ajax({
        url: "/web/hotwords/unique_id/test123/hotwords_type/" + hot_words_type,
        success: function (j) {
            console.log(j)
            if (j['error_code'] == 0) {
              // hot words
              hotwords = ""
              words = JSON.parse(j["data"]["words"].replace(/^\"|\"$/g,''))
              for (var i in words) {
                hotwords = hotwords + words[i]
                if (i != words.length - 1) {
                  hotwords = hotwords + "\n"
                }
              }
              $("#get_hot_words").val(hotwords);
            }
        }
    });
  });

  function checkField(val) {
    $.ajaxSetup({ "xhrFields": true });
    $.ajax({
        url: "/web/hotwords/unique_id/test123/hotwords_type/" + val,
        success: function (j) {
            if (j['error_code'] == 0) {
              // hot words
              hotwords = ""
              words = JSON.parse(j["data"]["words"].replace(/^\"|\"$/g,''))
              for (var i in words) {
                hotwords = hotwords + words[i]
                if (i != words.length - 1) {
                  hotwords = hotwords + "\n"
                }
              }
              $("#get_hot_words").val(hotwords);
            }
        }
    });
  }

  function tips(msg) {
    $("#tips_content").html(msg);
    $("#tips_show").css('display', '');
  }

  function check_rows(arr) {
    if (arr.length > 2000) {
      alert("Error:热词数量大于2000");
      return false;
    } else {
      return true;
    }
  }

  function check_every_row_str_length(arr) {
    for (var i = 0; i < arr.length; i++) {
      if (arr[i].length > 10) {
        alert("Error:存在某个热词字符数量大于10");
        return false;
      }
    }
    return true;
  }

  function check_special_char(arr) {
    var tr = /^[\u0391-\uFFE5A-Za-z\n]+$/;
    for (var i = 0; i < arr.length; i++) {
      if (!tr.test(arr[i])) {
        alert("Error:热词中存在数字或特殊字符！");
        return false;
      }
    }
    return true;
  }

  function sava_hot_words() {
    let words = $("#get_hot_words").val();
    res = words.split("\n");
    if (!check_rows(res)) {
      return;
    }
    if (!check_every_row_str_length(res)) {
      return;
    }
    if (!check_special_char(res)) {
      return;
    }
    console.log(res)
    // 获取类型
    hot_words_type = $("#hot_words_type option:selected").val();
    console.log(hot_words_type)
    var data = { "words": res, "unique_id": "test123", "type": hot_words_type }
    console.log(data)
    $.ajaxSetup({ "xhrFields": true });
    $.ajax({
      url: "/web/hotwords",
      data: JSON.stringify(data),
      contentType: "application/json",
      type: "Post",
      traditional: true,
      success: function (j) {
        if (j['error_code'] == 0) {
          alert("热词发布成功");
        } else {
          alert("热词发布失败");
        }
      }
    });
  }
*/



