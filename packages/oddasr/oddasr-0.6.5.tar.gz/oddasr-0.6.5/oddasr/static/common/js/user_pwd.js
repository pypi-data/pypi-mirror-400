$(function () {
    init();

    //init函数
  function init () {
    initEvent();
    initShowHidePass();
    clearTips("newPasswordTip");
    clearTips("rePasswordTip");
    $("#oldPassword").val("");
  }







    //主要操作函数
     function initEvent () {



            //密码框默认的提示信息
            $(".help").hover(function () {
                $(".help-info").toggleClass("displayNone");
            });

            //原始密码框的光标获得、失去事件
            $("#oldPassword").bind("focus", function () {
                $(".text-tips").hide();
                $(this).next().addClass("hide-password");
            }).bind("blur", function () {
                $(this).next().removeClass("hide-password");
            }).bind("keyup", function () {
                capitalTip("oldPassword");
                clearTips("oldPasswordTip");
            });


            var regex = /^\s+/
            var reg = /[a-zA-Z0-9\.\_\,]/g;//匹配字母（区分大小写）、数字、_ 、,
            //新密码框的光标获得、失去事件
            $("#newPassword").bind('blur', function () {
                $(this).next().removeClass("hide-password");
                var len = this.value.length;
                if (this.value == "") {
                    clearTips("newPasswordTip");
                    hideStrength();
                    showTips("newPasswordTip", false, "密码不能为空");
                    return false;
                }
                if (len < 8 || len > 16) {
                    clearTips("newPasswordTip");
                    hideStrength();
                    showTips("newPasswordTip", false, "密码长度不正确，应为8～16个字符");
                    return false;
                }
                var strong = $(".newPasswordTip").children("span[class*=tip-info]").text();
                if (strong === "强") {
                    var isright = ckeckIsAllChar(this.value);
                    if (!isright) {
                        clearTips("newPasswordTip");
                        hideStrength();
                        showTips("newPasswordTip", false, "密码不可全为特殊字符，至少包含其中两种");
                        return false;
                    }
                }
            }).bind('focus', function () {
                $(".text-tips").show();
                $(this).next().addClass("hide-password");
                $("#rePassword").val("");
                clearTips("rePasswordTip");
            }).bind('keyup', function () {
                if (regex.test(this.value)) {
                    hideStrength();
                    showTips("newPasswordTip", false, "新密码不可包含空格");
                } else {
                    var strong = checkPasswordLevel(this.value);
                    showStrength(strong);
                    capitalTip("newPassword");
                }
                ;

            });

            //确认密码框的光标获得、失去事件
            $("#rePassword").bind('blur', function () {
                $(this).next().removeClass("hide-password");
                if (this.value.length < 8 || this.value.length > 16) {
                    clearTips("rePasswordTip");
                    showTips("rePasswordTip", false, "密码长度不正确，应为8～16个字符");
                    return false;
                }
            }).bind('focus', function () {
                $(".text-tips").hide();
                $(this).next().addClass("hide-password");
                if (!$("#newPassword").val()) {
                    hideStrength();
                    showTips("newPasswordTip", false, "新密码不能为空");
                }
            }).bind('keyup', function () {
                capitalTip("rePassword");
                if (!($("#newPassword").val() == this.value)) {
                    clearTips("rePasswordTip");
                    showTips("rePasswordTip", false, "密码不一致");
                } else {
                    clearTips("rePasswordTip");
                    showTips("rePasswordTip", true, "密码一致");
                    return;
                }
            });

            //保存密码
            $(".update-btn").on("click",function(){
                changePwd();
            });



  function tips(msg){
      $("#tips_content").html(msg);
      $("#tips_show").css('display','');
      //alert(msg);
      //alert(document.getElementById("tips_content").outerHTML);
      //document.getElementById("tips_content").innerHTML = msg;
  }



  function changePwd(){
       var error = $("span[class*=error-icon]");
       var weak = $("span[class*=weak-icon]");
       if (weak.length > 0) {
           hideStrength();
           showTips("newPasswordTip", false, "密码强度需为中或中以上");
           return;
       }
       if (error.length > 0) {
            return;
       }

        $(".error_msg").hide();

        var oldPassword = $("#oldPassword");
        var oldPasswordVal = oldPassword.val();
        var newPassword = $("#newPassword");
        var newPasswordVal = newPassword.val();
        var rePassword = $("#rePassword");
        var rePasswordVal = rePassword.val();

        //判断新密码是否包含非法字符
        if (!(newPasswordVal.replace(reg, "").length == 0)) {
            hideStrength();
            showTips("newPasswordTip", false, "存在非法字符，请重新输入");
            return false;
        }
        if (oldPasswordVal == "") {
            clearTips("oldPasswordTip");
            showTips("oldPasswordTip", false, "密码不能为空");
            return false;
        }
        if (newPasswordVal == "") {
            clearTips("newPasswordTip");
            hideStrength();
            showTips("newPasswordTip", false, "密码不能为空");
            return false;
        }
        if (newPasswordVal.length < 8 || newPasswordVal.length > 16) {
            hideStrength();
            showTips("newPasswordTip", false, "密码长度不正确，应为8～16个字符");
            return false;
        }

        if (rePasswordVal.length == 0) {
            clearTips("rePasswordTip");
            showTips("rePasswordTip", false, "确认密码不能为空");
            return false;
        }

        if (newPasswordVal != rePasswordVal) {
            showTips("rePasswordTip", false, "两次输入的密码不一致，请重新输入");
            return false;
        }





        //then validate from server.
        $.ajaxSetup({"xhrFields" :true});
        $.ajax({
          url:"/pwd_change",
          data:JSON.stringify({'user':user , 'pwd':oldPasswordVal, 'newPwd':newPasswordVal}),
          contentType : "application/json",
          type:"Post",
          success:function(j){
            if(j['code'] == 0){
              tips("修改密码成功！");
               oldPassword.val("");
                newPassword.val("");
                rePassword.val("");
                hideStrength();
                clearTips("newPasswordTip");
                clearTips("oldPasswordTip");
                clearTips("rePasswordTip");
                $(".showHidePassword").removeClass("show-password");
                $(".text-tips").hide();
                $("#oldPassword").attr("type","password")
                $("#newPassword").attr("type","password")
                $("#rePassword").attr("type","password")
            }else{
              tips('用户名或密码不正确');
              clearTips("oldPasswordTip");
            }
          }
        });
  }



//            //保存密码
//            $("#setting-editpasswd-save").click(function () {
//                var error = $("span[class*=error-icon]");
//                var weak = $("span[class*=weak-icon]");
//                if (weak.length > 0) {
//                    hideStrength();
//                    showTips("newPasswordTip", false, "密码强度需为中或中以上");
//                    return;
//                }
//                if (error.length > 0) {
//                    return;
//                }
//                $("#setting-editpasswd").submit();
//            });

//            $("#setting-editpasswd").submit(function () {
//
//                if ($("#setting-editpasswd-save").hasClass("disabled")) {
//                    return false;
//                }
//
//
//                $(".error_msg").hide();
//                var url = this.action;
//                var oldPassword = $("#oldPassword");
//                var oldPasswordVal = oldPassword.val();
//                var newPassword = $("#newPassword");
//                var newPasswordVal = newPassword.val();
//                var rePassword = $("#rePassword");
//                var rePasswordVal = rePassword.val();
//
                //判断新密码是否包含非法字符
                //var reg = /[a-zA-Z0-9\#\*]/g;//匹配字母（区分大小写）、数字、* 、#
                // var reg = /[a-zA-Z0-9\.\_\,]/g;//匹配字母（区分大小写）、数字、_ 、,
//                if (!(newPasswordVal.replace(reg, "").length == 0)) {
//                    hideStrength();
//                    showTips("newPasswordTip", false, "存在非法字符，请重新输入");
//                    return false;
//                }
//                if (oldPasswordVal == "") {
//                    clearTips("oldPasswordTip");
//                    showTips("oldPasswordTip", false, "密码不能为空");
//                    return false;
//                }
//                if (newPasswordVal == "") {
//                    clearTips("newPasswordTip");
//                    hideStrength();
//                    showTips("newPasswordTip", false, "密码不能为空");
//                    return false;
//                }
//                if (newPasswordVal.length < 8 || newPasswordVal.length > 16) {
//                    hideStrength();
//                    showTips("newPasswordTip", false, "密码长度不正确，应为8～16个字符");
//                    return false;
//                }
//
//                if (rePasswordVal.length == 0) {
//                    clearTips("rePasswordTip");
//                    showTips("rePasswordTip", false, "确认密码不能为空");
//                    return false;
//                }
//
//                if (newPasswordVal != rePasswordVal) {
//                    showTips("rePasswordTip", false, "两次输入的密码不一致，请重新输入");
//                    return false;
//                }
//
//                $("#setting-editpasswd-save").addClass("disabled")
//                $.post(url, {
//                    moid: TS.cfg.USER.moid,
//                    oldPassword: oldPasswordVal,
//                    newPassword: newPasswordVal
//                }, function (t, type) {
//                    $("#setting-editpasswd-save").removeClass("disabled");
//                    if (t.success) {
//                        App.alertDialog("修改密码成功");
//                        oldPassword.val("");
//                        newPassword.val("");
//                        rePassword.val("");
//                        hideStrength();
//                        clearTips("newPasswordTip");
//                        clearTips("oldPasswordTip");
//                        clearTips("rePasswordTip");
//                        return;
//                    } else {
//                        clearTips("oldPasswordTip");
//                        showTips("oldPasswordTip", false, t.description);
//                    }
//
//                }, 'json');
//                return false;
//            });
        }



//  --------------------------------------------------------------------------------------



  //  点击小眼睛，切换password和text
    function  initShowHidePass() {
        $(".showHidePassword").mousedown(function () {
            toggleEye($(this))
        });
    }



    function showError(obj, msg) {
        obj.next(".tip-icon").removeClass("correct-icon").addClass("error-icon");
        obj.next(".tip-icon").next(".tip-info").removeClass("correct-tip").addClass("error-tip");
        obj.next(".tip-icon").next(".tip-info").text(msg);
    }



    function showTips(typeofPasswordTip, isCorrect, tips) {
        if (isCorrect) {
            $("." + typeofPasswordTip + " .tip-icon").removeClass("error-icon").addClass("correct-icon");
            $("." + typeofPasswordTip + " .tip-info").removeClass("error-tip").addClass("correct-tip");
            $("." + typeofPasswordTip + " .tip-info").text(tips);
        } else {
            $("." + typeofPasswordTip + " .tip-icon").removeClass("correct-icon").addClass("error-icon");
            $("." + typeofPasswordTip + " .tip-info").removeClass("correct-tip").addClass("error-tip");
            $("." + typeofPasswordTip + " .tip-info").text(tips);
        }
    }




    //  清除输入框的错误提示的文字和icon
    function clearTips(typeofPasswordTip) {
        $("." + typeofPasswordTip + " .tip-icon").removeClass("error-icon correct-icon");
        $("." + typeofPasswordTip + " .tip-icon").removeClass("error-tip correct-tip");
        $("." + typeofPasswordTip + " .tip-info").text("");
    }

    function showStrength(strong) {
        $(".help").show();
        if (strong == "weak") {
            $(".newPasswordTip .tip-icon").removeClass("medium-icon strong-icon error-icon");
            $(".newPasswordTip .tip-info").removeClass("medium-tip strong-tip");
            $(".newPasswordTip .tip-icon").addClass("weak-icon");
            $(".newPasswordTip .tip-info").addClass("weak-tip");
            $(".newPasswordTip .tip-info").text("弱");
        }
        if (strong == "medium") {
            $(".newPasswordTip .tip-icon").removeClass("weak-icon strong-icon error-icon");
            $(".newPasswordTip .tip-info").removeClass("weak-tip strong-tip");
            $(".newPasswordTip .tip-icon").addClass("medium-icon");
            $(".newPasswordTip .tip-info").addClass("medium-tip");
            $(".newPasswordTip .tip-info").text("中");
        }
        if (strong == "strong") {
            $(".newPasswordTip .tip-icon").addClass("strong-icon");
            $(".newPasswordTip .tip-icon").removeClass("error-icon weak-icon");
            $(".newPasswordTip .tip-info").addClass("strong-tip");
            $(".newPasswordTip .tip-info").text("强");
        }
        if (strong == "fault") {
            hideStrength();
            showTips("newPasswordTip", false, "密码不符合要求")
        }
    }


    function hideStrength() {
        $(".help").hide();
        $(".newPasswordTip .tip-icon").removeClass("weak-icon medium-icon strong-icon");
        $(".newPasswordTip .tip-info").removeClass("weak-tip medium-tip strong-tip");
        $(".newPasswordTip .tip-info").text("");
    }

    //  点击小眼睛，切换password和text
    function toggleEye($this) {
        $this.toggleClass("show-password");
        if ($this.hasClass("show-password")) {
            $this.prev()[0].type = "text";
        } else {
            $this.prev()[0].type = "password";
        }
    }

     function getBytesLength(str) {
        // 在GBK编码里，除了ASCII字符，其它都占两个字符宽
        return str.replace(/[^\x00-\xff]/g, 'xx').length;
    }

       //检查密码强度
    function checkCharMode(ch) {
        if (ch >= 48 && ch <= 57) {//数字
            return 1;
        } else if (ch >= 65 && ch <= 90) {//大写字母
            return 2;
        } else if (ch >= 97 && ch <= 122) {//小写字母
            return 4;
        } else {//特殊字符 : _ 是95；.是46
            if (ch == 95 || ch == 46) {
                return 8;
            } else {
                return 9;
            }
        }
    }

    function ckeckIsAllChar(value) {
        for (var i = 0; i < value.length; i++) {
            var ch = value.charCodeAt(i);
            if (ch >= 48 && ch <= 57 || ch >= 65 && ch <= 90 || ch >= 97 && ch <= 122) {
                return true;
            }
        }
        return false;
    }

    function checkPasswordLevel(value) {
        var strong = 0;
        for (var i = 0; i < value.length; i++) {
            if (checkCharMode(value.charCodeAt(i)) == 9) {
                strong = -1;
                break;
            }
            if (checkCharMode(value.charCodeAt(i)) == 8) {
                strong++;
            }
        }
        if (strong == 1) {
            return "medium";
        } else if (strong > 1) {
            return "strong";
        } else if (strong == -1) {
            return "fault";
        } else {
            return "weak";
        }
    }

    //密码大写输入提示
    function capitalTip(id) {
        var capital = false; //聚焦初始化，防止刚聚焦时点击Caps按键提示信息显隐错误
        // 获取大写提示的标签，并提供大写提示显示隐藏的调用接口
        var capitalTip = {
            $elem: $('#capital_' + id),
            toggle: function (s) {
                if (s === 'none') {
                    this.$elem.hide();
                } else if (s === 'block') {
                    this.$elem.show();
                } else if (this.$elem.is(':hidden')) {
                    this.$elem.show();
                } else {
                    this.$elem.hide();
                }
            }
        };
        $('#' + id).on('keydown.caps', function (e) {
            if (e.keyCode === 20 && capital) { // 点击Caps大写提示显隐切换
                capitalTip.toggle();
            }
        }).on('focus.caps', function () {
            capital = false
        }).on('keypress.caps', function (e) {
            capsLock(e)
        }).on('blur.caps', function (e) {

            //输入框失去焦点，提示隐藏
            capitalTip.toggle('none');
        });

        function capsLock(e) {
            var keyCode = e.keyCode || e.which;// 按键的keyCode
            var isShift = e.shiftKey || keyCode === 16 || false;// shift键是否按住
            if (keyCode === 9) {
                capitalTip.toggle('none');
            } else {
                //指定位置的字符的 Unicode 编码 , 通过与shift键对于的keycode，就可以判断capslock是否开启了
                // 90 Caps Lock 打开，且没有按住shift键
                if (((keyCode >= 65 && keyCode <= 90) && !isShift) || ((keyCode >= 97 && keyCode <= 122) && isShift)) {
                    capitalTip.toggle('block'); // 大写开启时弹出提示框
                    capital = true;
                } else {
                    capitalTip.toggle('none');
                    capital = true;
                }
            }
        }
    }




    function changeTipStyle(obj) {
        obj.next(".tip-icon").removeClass("error-icon");
        obj.next(".tip-icon").next(".tip-info").removeClass("error-tip").addClass("correct-tip");
    }

    function reSetTipStyle(obj) {
        obj.next(".tip-icon").removeClass("error-icon");
        obj.next(".tip-icon").next(".tip-info").removeClass("error-tip correct-tip");
        obj.next(".tip-icon").next(".tip-info").text("");
    }











//    -----------------------------------------------------------------------------------------------




});