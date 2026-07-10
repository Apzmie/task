const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

const themeBtn = document.querySelector(".theme-btn");

const navbar = document.querySelector(".navbar");

const topBtn = document.querySelector("#top-btn");

const projectList = document.querySelector("#project-list");

const form = document.querySelector("#contact-form");



// =======================
// 햄버거 메뉴
// =======================

hamburger.addEventListener("click",()=>{

    navMenu.classList.toggle("active");

});



// =======================
// 다크모드 상태
// =======================

const savedTheme = localStorage.getItem("theme");


if(savedTheme){

    document.documentElement.dataset.theme=savedTheme;

}



themeBtn.addEventListener("click",()=>{


const current =
document.documentElement.dataset.theme;


const next =
current==="dark"
?"light"
:"dark";


document.documentElement.dataset.theme=next;


localStorage.setItem(
"theme",
next
);



});




// =======================
// 스크롤 이벤트
// =======================


window.addEventListener("scroll",()=>{


if(window.scrollY>60){

navbar.classList.add("scrolled");

}

else{

navbar.classList.remove("scrolled");

}



if(window.scrollY>300){

topBtn.style.display="block";

}

else{

topBtn.style.display="none";

}



});



topBtn.addEventListener("click",()=>{


window.scrollTo({

top:0,

behavior:"smooth"

});


});





// =======================
// Intersection Observer
// =======================


const observer =
new IntersectionObserver(
(entries)=>{


entries.forEach(
(entry)=>{


if(entry.isIntersecting){

entry.target.classList.add("active");

}


});


},
{

threshold:0.2

});


document
.querySelectorAll(".reveal")
.forEach(
(element)=>observer.observe(element)
);







// =======================
// GitHub API
// =======================


const username="본인아이디";


const loadProjects = async()=>{


projectList.innerHTML=
"<p>로딩 중...</p>";



try{


const response =
await fetch(
`https://api.github.com/users/${username}/repos`
);



if(!response.ok){

throw new Error();

}



const repos =
await response.json();





const filtered =
repos.filter(
(repo)=>!repo.fork
);




if(filtered.length===0){

projectList.innerHTML=
"<p>표시할 프로젝트가 없습니다.</p>";

return;

}




projectList.innerHTML =
filtered.map(
(repo)=>{


const {
name,
html_url,
description,
stargazers_count
}=repo;



return `

<article class="project-card">

<h3>${name}</h3>

<p>
${description ?? "설명 없음"}
</p>


<p>
⭐ ${stargazers_count}
</p>


<a href="${html_url}" target="_blank">
보기
</a>


</article>

`;

}

).join("");



}

catch(error){


projectList.innerHTML=`

<p>
프로젝트를 불러올 수 없습니다.
</p>

<button id="retry">
다시 시도
</button>

`;


document
.querySelector("#retry")
.addEventListener(
"click",
loadProjects
);


}



};


loadProjects();






// =======================
// Contact Form Validation
// =======================


form.addEventListener(
"submit",
(event)=>{


event.preventDefault();



const name =
document.querySelector("#name").value.trim();


const email =
document.querySelector("#email").value.trim();


const message =
document.querySelector("#message").value.trim();



let valid=true;



document.querySelector("#name-error")
.textContent="";


document.querySelector("#email-error")
.textContent="";


document.querySelector("#message-error")
.textContent="";




if(!name){

document.querySelector("#name-error")
.textContent="이름을 입력하세요";

valid=false;

}



const emailRegex =
/^[^\s@]+@[^\s@]+\.[^\s@]+$/;



if(!emailRegex.test(email)){


document.querySelector("#email-error")
.textContent="올바른 이메일 형식이 아닙니다";


valid=false;


}



if(!message){


document.querySelector("#message-error")
.textContent="메시지를 입력하세요";


valid=false;


}



if(valid){


document.querySelector("#success-message")
.textContent=
"성공적으로 제출되었습니다.";


form.reset();


}



});
