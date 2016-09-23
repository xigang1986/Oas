/**
 * Created by 张晓宇 on 2016/5/4.
 * 左侧导航模块，通用类代码，整个应用的适用
 */

$(function (){
    $('.item').each(function (){
        if($(this).hasClass('active') == false){
            console.log(this);
            $(this).children('div').addClass('hide');
        }else{
            $(this).children('li').children('i').removeClass('fa-angle-left');
            $(this).children('li').children('i').addClass('fa-angle-down');
        }
    });
    $('.level-one').click(function (){
        console.log($(this).children('li'));
        if(!$(this).parent().hasClass('active')){
            $(this).siblings().removeClass('hide');
            $(this).siblings().addClass("animated");
            $(this).siblings().addClass('fadeInLeft');
            $(this).parent().addClass('active');
            $(this).children('i').removeClass('fa-angle-left');
            $(this).children('i').addClass('fa-angle-down');
        }else{
            $(this).siblings().addClass('hide');
            $(this).parent().removeClass('active');
            $(this).children('i').removeClass('fa-angle-down')
            $(this).children('i').addClass('fa-angle-left')
        }

    });
});
