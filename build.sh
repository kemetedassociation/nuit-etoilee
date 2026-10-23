#!/bin/sh
# Assemble index.html (site autonome) à partir de page.html
cd "$(dirname "$0")"
{
  printf '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="theme-color" content="#0a0c13">\n<meta name="description" content="Nuit Étoilée — dix contes du monde à écouter, avec quiz, énigmes et mini-jeux. KEMETED & Association.">\n<link rel="manifest" href="manifest.json">\n<link rel="icon" href="img/icone.png">\n'
  cat page.html
  printf '\n<script>if("serviceWorker" in navigator && location.protocol.startsWith("http")) {var avait=!!navigator.serviceWorker.controller;navigator.serviceWorker.register("sw.js").catch(function(){});navigator.serviceWorker.addEventListener("controllerchange",function(){try{if(avait&&!sessionStorage.getItem("ne-maj")){sessionStorage.setItem("ne-maj","1");location.reload();}}catch(e){}});}</script>\n</html>\n'
} > index.html
echo "index.html généré"
