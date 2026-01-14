
class ObjectSet extends Set {
    add(elem){
        return super.add(typeof elem === 'object' ? JSON.stringify(elem) : elem);
    }
    has(elem){
        return super.has(typeof elem === 'object' ? JSON.stringify(elem) : elem);
    }
}

const FIXES = Object.freeze({
        "NEW_CERT":   "Faire émettre de nouveaux certificats",
        "CAA":  "Mettre en place un enregistrement DNS CAA",
        "INTERMEDIATE_CERT":  "Ajouter les certificats intermédiaires",
        "ALT_CERT" : "Ajouter des certificats alternatifs",
});

const testsslresults = async() => {
    let is_sncf = false;
    try{
        let pentest_settings = await api.getPentestSettings();
         // Check if the client is SNCF
        if (api.extractSetting(pentest_settings.data, "client_name").toLowerCase().includes("sncf")) {
            is_sncf = true;
        }
    }
    catch (error) {
        api.log({
            title: "Error",
            description: "Error fetching pentest settings",
            status: "error",
            duration: 3000,
            isClosable: true,
        });            
    }

    // Get tags and ports
    const tags_data = (await api.findInDb("tags", { "tags.name": "SSL/TLS-flaws" }, true)).data;
    const port_ids = [];
    for (let tag of tags_data) {
        if (tag.item_type === "ports") {
            port_ids.push(tag.item_id);
        }
    }
    const expectedVulns = ["SSLv2","SSLv3","TLS1","TLS1_1","TLS1_2","TLS1_3","FS","cipherlist_NULL","cipherlist_aNULL","cipherlist_EXPORT","cipherlist_DES+64Bit","cipherlist_128Bit","cipherlist_3DES","cipher_order","secure_renego","secure_client_renego","fallback_SCSV","heartbleed","ticketbleed","CCS","ROBOT","POODLE_SSL","CRIME_TLS","BREACH","SWEET32","FREAK","DROWN","LOGJAM","BAR_MITZVAH","LUCKY13","RC4","BEAST","BEAST_CBC_TLS1"];

    const list_of_all_ports = (await api.findInDb("ports", { "_id": { "$in": port_ids } }, true)).data;

    // Craft list of all the lines returned by testssl.sh from the port info
    let list_of_all_lines = [];
    let list_of_defects = [];
    let dict_line = {};
    for (let port of list_of_all_ports) {
        list_of_defects = port.infos["TestSSL"];
        if (list_of_defects === undefined) {
            continue;
        }
        expectedVulns.forEach((defect_id) => {
            if (!list_of_defects.some((defect) => defect.defect === defect_id)) {

                list_of_defects.push({defect: defect_id, criticity: "OK", details: ""});
            }
        });

        for (let vuln of list_of_defects) {
            dict_line = {"ip": port.ip, "port": port.port, "domain": port.infos.FQDN, "defect": vuln.defect, "criticity": vuln.criticity, "details": vuln.details};
            list_of_all_lines.push(dict_line);
        }
    }
 
    const vulnDataList = [];
    const completeData = [];
    var newTLSDefect = new ObjectSet();

    // Get certificate lifespan
    var notAfter = undefined;
    var notBefore = undefined;
    var lifespan = -1;

    var keySizeInfo;
    
    // avoid adding the same defect multiple times
    let TLSv1_0_or_1_1 = false;
    let already_added = false;
   

    for (let vuln of list_of_all_lines) {
        // CERTIFICATES //
        // Get certificate common name
        if (["cert_commonName", "cert_commonName <hostCert#1>"].includes(vuln.defect)) {
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Common Name", "vulnerable": "no", "state": vuln.details});
        }
        // Get cetificate alternative names
        else if (["cert_subjectAltName", "cert_subjecAltName <hostCert#1>"].includes(vuln.defect)) {
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Alternative Name(s)", "vulnerable": "no", "state": vuln.details});
        }
        // Get certificate Validity left
        else if (["cert_expirationStatus", "cert_expirationStatus <hostCert#1>"].includes(vuln.defect)) {
            if (!["OK", "INFO"].includes(vuln.criticity)){
               if (vuln.details === "expired"){
                    newTLSDefect.add(["Certificat expiré", FIXES.NEW_CERT]);
                    vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate "+vuln.details,  "criticity": vuln.criticity});

                    completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Validity Left", "vulnerable": "yes", "state": vuln.details});
                }
                else{
                    vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate "+vuln.details,  "criticity": vuln.criticity});
                    completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Validity Left", "vulnerable": "yes", "state": vuln.details});
                
                }
            }
            else{
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Validity Left", "vulnerable": "no", "state": vuln.details});
            }
        }
        // Get notAfter date
        else if (["cert_notAfter", "cert_notAfter <hostCert#1>"].includes(vuln.defect)) {
            notAfter = new Date(vuln.details);
        }
        // Get notBefore date
        else if (["cert_notBefore", "cert_notBefore <hostCert#1>"].includes(vuln.defect)) {
            notBefore = new Date(vuln.details);
        }
        // Calculate certificate lifespan
        else if (notAfter !== undefined && notBefore !== undefined && lifespan === -1) {
            lifespan = Math.round(Math.abs(notAfter - notBefore) / 86400000);
            if (lifespan > 398){
                newTLSDefect.add(["Durée de validité du certificat trop longue", FIXES.NEW_CERT]);
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Total Lifespan", "vulnerable": "yes", "state": lifespan + " days"});
                continue
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Total Lifespan", "vulnerable": "no", "state": lifespan + " days"});
            lifespan = -1; // Reset lifespan for next certificate
            notAfter = undefined; // Reset notAfter for next certificate
            notBefore = undefined; // Reset notBefore for next certificate
        }
        // Get certificate signature algorithm
        else if (["cert_signatureAlgorithm", "cert_signatureAlgorithm <hostCert#1>"].includes(vuln.defect)) {
            if ([ "OK", "INFO"].includes(vuln.criticity) === false){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate "+vuln.details, "criticity": vuln.criticity});
                if (vuln.details.includes("SHA1")){
                    newTLSDefect.add(["Certificat signé en SHA-1", FIXES.NEW_CERT]);
                    completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Signature Algorithm", "vulnerable": "yes", "state": vuln.details});
                    continue;
                }
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Signature Algorithm", "vulnerable": "no", "state": vuln.details});
        }
        // Get Certificate key size
        else if (["cert_keySize", "cert_keySize <hostCert#1>"].includes(vuln.defect)) {
            if ([ "OK", "INFO"].includes(vuln.criticity) === false){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate "+vuln.details, "criticity": vuln.criticity});
                keySizeInfo = vuln.details.split(" ");
                if ((keySizeInfo[0] === "RSA" && parseInt(keySizeInfo[1]) < 2048) || (keySizeInfo[0] === "EC" && parseInt(keySizeInfo[1]) < 256)){
                    newTLSDefect.add(["Taille de clé trop faible", FIXES.NEW_CERT]);
                    completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Key Size", "vulnerable": "yes", "state": vuln.details});
                    continue;
                }
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Key Size", "vulnerable": "no", "state": vuln.details});
        }
        // Get certificate issuer
        else if (["cert_caIssuers", "cert_caIssuers <hostCert#1>"].includes(vuln.defect)) {
            // Check if the issuer is DigiCert for SNCF only
            if (is_sncf && !vuln.details.toLowerCase().includes("digicert")){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate issuer is not DigiCert (SNCF only)", "criticity": "INFO"});
                newTLSDefect.add(["Certificat émis par une autorité de certification non approuvée", FIXES.NEW_CERT]);
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Issuer", "vulnerable": "yes", "state": vuln.details});
                continue;
            }
            // Check if the issuer is emmited by a private CA or self-signed (not for SNCF)
            if ((vuln.details.toLowerCase().includes("selfsigned") || vuln.details.toLowerCase().includes("private")) && !is_sncf){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate issuer is self-signed or private", "criticity": "INFO"});
                newTLSDefect.add(["Certificat émis par une autorité de certification privée ou auto-signé", FIXES.NEW_CERT]);
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Issuer", "vulnerable": "yes", "state": vuln.details});
                continue;
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Issuer", "vulnerable": "no", "state": vuln.details});
        }
        // Revocation list enabled ?
        else if (["cert_crlDistributionPoints", "cert_crlDistributionPoints <hostCert#1>"].includes(vuln.defect)) {
            if (!["OK", "INFO"].includes(vuln.criticity)){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate Revocation List Disabled", "criticity": vuln.criticity});
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Revocation List", "vulnerable": "yes", "state": "Disabled"});
                newTLSDefect.add(["Absence de liste de révocation", FIXES.NEW_CERT]);
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Revocation List", "vulnerable": "no", "state": "Enabled"});
        }
        // CA authorisation
        else if (["DNS_CAArecord", "DNS_CAArecord <hostCert#1>"].includes(vuln.defect)) {
            if ((["OK", "INFO"].includes(vuln.criticity) === false)){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "No CA Authorisation", "criticity": vuln.criticity});
                newTLSDefect.add(["Pas d’autorisation d'Autorités de Certification (CAA)", FIXES.CAA]);
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "CA Authorisation", "vulnerable": "yes", "state": "No CAA record found"});
                continue;
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "CA Authorisation", "vulnerable": "no", "state": vuln.details});
        }
        // Transparancy
        else if (["certificate_transparency", "certificate_transparency <hostCert#1>"].includes(vuln.defect)) {
            if (!["OK", "INFO"].includes(vuln.criticity)){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Certificate Transparancy Disabled", "criticity": vuln.criticity});
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Transparency", "vulnerable": "yes", "state": "Disabled"});
                newTLSDefect.add(["Pas de Certificate Transparency", FIXES.NEW_CERT]);
                continue;
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Transparency", "vulnerable": "no", "state": "Enabled"});
        }
        // Chain of trust (SNCF is not concerned by this defect)
        else if (["cert_chain_of_trust", "cert_chain_of_trust <hostCert#1>"].includes(vuln.defect)) {
            if (!["OK", "INFO"].includes(vuln.criticity)){
                vulnDataList.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "defect": "Chain of Trust Incomplete", "criticity": vuln.criticity});
                completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Chain of Trust", "vulnerable": "yes", "state": "Incomplete"});
                if (!is_sncf){
                    newTLSDefect.add(["Chaîne de confiance incomplète", FIXES.INTERMEDIATE_CERT]);
                }
                continue;
            }
            completeData.push({"ip": vuln.ip, "port": vuln.port, "domain": vuln.domain, "about": "Chain of Trust", "vulnerable": "no", "state": "Verified"});
        }

    };

    newTLSDefect = Array.from(newTLSDefect);
    newTLSDefect = newTLSDefect.map(JSON.parse)

    return {vulnTable:vulnDataList, allDataForExcel:completeData, newTLSDefectForReport:newTLSDefect};

}
function updateTLSDefect(defectTLS, new_defect, defect_to_keep, fixes_to_keep) {
    const defectTLS_description = defectTLS.description;
    if (!new_defect.description) {
        new_defect.description = defectTLS_description.split("\r\n\r\n")[0] + "\r\n\r\n";
    }
    const lignes = defectTLS_description.split("\r\n\r\n");
    let title = "";
    for (const ligne of lignes) {
        if (ligne.startsWith("#")) {
            title = ligne.replace(/^#+\s*/, "").trim();
            if (title.includes(defect_to_keep)) {
                new_defect.description += ligne + "\r\n\r\n";
                continue;
            }
        }
        if (title.includes(defect_to_keep)) {
            new_defect.description += ligne + "\r\n\r\n";
        }
    }
    let fixes_array = fixes_to_keep;
    if (typeof fixes_to_keep === "string") {
        fixes_array = [fixes_to_keep];
    }
    const defectTLS_fixes = defectTLS.fixes || [];
    for (const fix of defectTLS_fixes) {
        if (fixes_array.includes(String(fix.title)) && !new_defect.fixes.some(f => f.title === fix.title)) {
            new_defect.fixes.push(fix);
        }
    }
    return new_defect;
}
async function generateDefect(newTLSDefect) {

    // Function to generate a defect in the report
    
    try {
        const defectTLS = await api.getCurrentDefect();
        
        let new_TLS_defect = {
            description: "",
            fixes: []
        };
        
        for (const d of newTLSDefect) {
            new_TLS_defect = updateTLSDefect(defectTLS, new_TLS_defect, d[0], d[1]);
        }
        
        defectTLS.description = new_TLS_defect.description;
        defectTLS.fixes = new_TLS_defect.fixes;
        
        // Remove _id if present to avoid conflicts
        if (defectTLS._id) {
            delete defectTLS._id;
        }
        
        await api.updateCurrentDefect(defectTLS);
        
        return { status: "success", data: defectTLS };
    } catch (error) {
        api.log( error.message);
        return { status: "error", message: error.message };
    }
}

const handleOnExport = (excelData) => {

    // Set empty worksheet
    let Ips = [];
    let columnHeaders = ["IP", "Port", "Domain"];

    let table = [["IP", "Port", "Domain"]];
    let colorTable = [["no", "no", "no"]];
    
    for (let data of excelData) {
        let row_index = Ips.indexOf(data.ip+"/"+data.port);

        // Add IP and Port to the worksheet everytime we find a new IP
        if (row_index === -1) {
            row_index = Ips.length;
            Ips.push(data.ip + "/"+data.port);
            const new_row = Array(columnHeaders.length).fill("");
            new_row[0] = data.ip;
            new_row[1] = data.port;
            new_row[2] = data.domain || "N/A"
            table.push(new_row);
            colorTable.push(["no", "no", "no"])
        }

        // Add defect headers dynamically
        if (!columnHeaders.includes(data.about)){
            columnHeaders.push(data.about);
            table[0].push(data.about);
        }
        // Set the defect data in the correct row and column 
        let column_index = columnHeaders.indexOf(data.about);
        table[row_index + 1][column_index] = data.state;
        colorTable[row_index + 1][column_index] = data.vulnerable;

    }        
    
    // Create a new worksheet
    let ws = api.XLSX.utils.aoa_to_sheet(table);
    let wb = api.XLSX.utils.book_new();

    // Color all the headers
    for (let i = 0; i < columnHeaders.length; i++) {
        let cell_ref = api.XLSX.utils.encode_cell({c: i, r: 0});
        ws[cell_ref].s = {fill: {patternType: "solid", fgColor: {rgb: "95cd41"} }, alignment: {horizontal: "center", vertical: "center"}, font: {bold: true} };
    }

    // Specify column width
    ws["!cols"] = [];
    for (let i = 0; i < columnHeaders.length; i++) {
        let max_lenght = columnHeaders[i].length;
        for (let j = 1; j < table.length; j++) {
            try{
                if (table[j][i].length > max_lenght) {
                    max_lenght = table[j][i].length;
                }
            
                let cell_ref = api.XLSX.utils.encode_cell({c: i, r: j});
                ws[cell_ref].s = {alignment: {horizontal: "center", vertical: "center"} };
                // center text in cell
                if (colorTable[j][i] === "yes") {
                    // Set font color in red and bold
                    ws[cell_ref].s = {font: {color: {rgb: "FF0000"}, bold: true }, alignment: {horizontal: "center", vertical: "center"}};
                }
            } catch (error) {
                console.log("Error:", error);
            }
        }
        let size = max_lenght * 1.2;
        // center text in colomn and set the width
        let col = {wch: size};
        ws["!cols"].push(col);
    }

    // Specify row height
    ws["!rows"] = [{hpt: 15}]; // set the first row height (header row)
    for (let i = 1; i < table.length; i++) {
        let row = {hpt: 50};
        ws["!rows"].push(row);
        
    }

    api.XLSX.utils.book_append_sheet(wb, ws, "TestSSL Report");
    api.XLSX.writeFile(wb, "TestSSL_Report.xlsx");
};

let results = await testsslresults();
if (typeof results !== 'undefined') {
    const list_of_defects = results.vulnTable;
    api.log("Défauts trouvés:");
    if (Array.isArray(list_of_defects) && list_of_defects.length) {
        const uniqueDefects = [...new Set(list_of_defects.map(d => d.defect))];
        api.log(uniqueDefects.join('\n'));
    } else {
        api.log("Aucun défaut détecté.");
    }
    let confirmed = await api.askyesno(
        "Est-ce que tu veux rédiger le défaut avec les informations de testssl ?",
        "Confirmation requise"
    );
    if (confirmed) {
        let generated_results = await generateDefect(results.newTLSDefectForReport);
        if (generated_results.status == "success"){
            api.log("Défaut créé avec succès.");
        }
        else{
            api.log("Échec de la création du défaut");
        }
    }
    else{
        api.log("Abandon de la rédaction du défaut.");
    }
    confirmed = await api.askyesno(
        "Est-ce que tu veux exporter les résultats de testssl vers un fichier Excel ?",
        "Confirmation requise"
    );
    if (confirmed) {
        handleOnExport(results.allDataForExcel);
        api.log("Exportation terminée.");
    }
    else{
        api.log("Abandon de l'exportation des résultats.");
    }
}
else{
    api.log("No testssl results found");
}