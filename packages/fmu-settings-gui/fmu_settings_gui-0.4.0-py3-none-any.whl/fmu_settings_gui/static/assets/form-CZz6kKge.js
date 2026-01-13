import{d as b,r as x,j as e,y as B}from"./index-CGCOPtAd.js";import{c as f,T as E,f as F,a as h,S,G as T,C as D,k}from"./field-B5157bDc.js";import{h as y}from"./validator-BVcLZbLS.js";const R=b.div`
  form > div {
    margin-bottom: 1em;
  }

  button + button {
    margin-left: 8px;
  }
`,V=b.div`
  display: flex;
  gap: 8px;
`,{useAppForm:G}=f({fieldContext:F,formContext:h,fieldComponents:{TextField:E},formComponents:{CancelButton:D,GeneralButton:T,SubmitButton:S}});function O({name:s,label:n,value:i,placeholder:l,helperText:a,length:o,minLength:d,mutationCallback:j,mutationIsPending:C}){const[p,m]=x.useState(!0),[v,g]=x.useState(!0),c=y({length:o,minLength:d}),A=({message:t,formReset:u})=>{B.info(t),u(),m(!0)},r=G({defaultValues:{[s]:i},onSubmit:({formApi:t,value:u})=>{j({formValue:u,formSubmitCallback:A,formReset:t.reset})}});return e.jsx(R,{children:e.jsxs("form",{onSubmit:t=>{t.preventDefault(),t.stopPropagation(),r.handleSubmit()},children:[e.jsx(r.AppField,{name:s,...c&&{validators:{onBlur:c}},children:t=>e.jsx(t.TextField,{label:n,placeholder:l,helperText:a,isReadOnly:p,setSubmitDisabled:g})}),e.jsx(r.AppForm,{children:p?e.jsx(r.GeneralButton,{label:"Edit",onClick:()=>{m(!1)}}):e.jsxs(e.Fragment,{children:[e.jsx(r.SubmitButton,{label:"Save",disabled:v,isPending:C,helperTextDisabled:"Value can be submitted when it has been changed and is valid"}),e.jsx(r.CancelButton,{onClick:t=>{t.preventDefault(),r.reset(),m(!0)}})]})})]})})}const{useAppForm:P}=f({fieldContext:F,formContext:h,fieldComponents:{SearchField:k},formComponents:{SubmitButton:S}});function U({name:s,value:n,helperText:i,setStateCallback:l}){const a=P({defaultValues:{[s]:n},onSubmit:({formApi:o,value:d})=>{l(d[s]),o.reset()}});return e.jsx("form",{onSubmit:o=>{o.preventDefault(),o.stopPropagation(),a.handleSubmit()},children:e.jsxs(V,{children:[e.jsx(a.AppField,{name:s,children:o=>e.jsx(o.SearchField,{helperText:i,toUpperCase:!0})}),e.jsx(a.AppForm,{children:e.jsx(a.SubmitButton,{label:"Search"})})]})})}export{O as E,U as S};
