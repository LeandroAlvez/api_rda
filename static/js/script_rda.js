var nomeVeiculoPDF;
let nomeArquivo_pdf;
$(document).ready(function() {
    // Função para preencher a lista suspensa de veículos com base no tipo selecionado
    function atualizarVeiculos(tipoVeiculo) {
        // Limpar a lista suspensa de veículos
        var veiculoSelect = $('#veiculo');
        veiculoSelect.empty();

        // Fazer a requisição AJAX para obter a lista de veículos correspondentes ao tipo selecionado
        $.ajax({
            url: '/filtro_veiculo',
            type: 'GET',
            data: { tipo_veiculo: tipoVeiculo },
            success: function(data) {
                // Preencher a lista suspensa de veículos com os valores retornados
                var veiculos = data;
                for (var i = 0; i < veiculos.length; i++) {
                    veiculoSelect.append('<option value="' + veiculos[i] + '">' + veiculos[i] + '</option>');
                }
            }
        });
    }
    // Fazer a requisição AJAX para obter a lista de tipos de veículos
    $.ajax({
        url: '/filtro_tipo_veiculo',
        type: 'GET',
        success: function(data) {
            // Preencher a lista suspensa de tipos de veículos com os valores retornados
            var tipoVeiculos = data;
            var tipoVeiculoSelect = $('#tipo_veiculo');
            for (var i = 0; i < tipoVeiculos.length; i++) {
                tipoVeiculoSelect.append('<option value="' + tipoVeiculos[i] + '">' + tipoVeiculos[i] + '</option>');
            }

            // Definir o evento de mudança no campo tipo_veiculo
            tipoVeiculoSelect.on('change', function() {
                var tipoVeiculoSelecionado = $(this).val();
                atualizarVeiculos(tipoVeiculoSelecionado);
            });
        }
    });

    $('form').on('submit', function(event) {
        event.preventDefault(); // Impedir o comportamento padrão do formulário

        // Obter os valores dos campos de data e veículo selecionados
        var dataInicio = $('#data_inicio').val();
        var dataFim = $('#data_fim').val();
        var veiculo = $('#veiculo').val();

  
        let dataInicioDate = new Date(dataInicio + 'T00:00');
        var nomeMesInicio = dataInicioDate.toLocaleString('default', {month: 'long' });
        var anoInicio = dataInicioDate.getFullYear();
        let dataFimDate = new Date(dataFim + 'T00:00');
        var nomeMesFim = dataFimDate.toLocaleString('default', {month: 'long'});
        var anoFim = dataFimDate.getFullYear();
        var nome_veiculo = veiculo
        var frase_titulo = veiculo + '  -  ' + letraMaiuscula(nomeMesInicio) + ' de ' + anoInicio + ' a ' + letraMaiuscula(nomeMesFim) + ' de ' + anoFim;
        $('#nome_veiculo_selecionado').html('<span>'+ frase_titulo + '</sapn>');
        nomeVeiculoPDF = nome_veiculo
        nomeArquivoPDF = $('#nome_veiculo_selecionado').html('<span>'+ frase_titulo + '</sapn>');
        console.log(nomeArquivo_pdf)
        let diferencaMeses = (dataFimDate.getFullYear()- dataInicioDate.getFullYear()) * 12 + (dataFimDate.getMonth() - dataInicioDate.getMonth());
        if (diferencaMeses > 5 ) {
            alert('A diferença entre as datas não podem ser superior a 6 meses! Por favor escolha outra data final.');
            $('#data_fim').val('');  
        } else {
            $('#loader').removeClass('hidden');
            $('#overlay').removeClass('hidden');

            function verificarRequestsFinalizadas() {
                if(requestsFinalizadas === 6) {
                    $('#relatorio-container').removeClass('hidden')
                }
            }
            var requestsFinalizadas = 0;

            $.ajax({
                url: '/dados_atendimento',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    preencherDadosAtendimento(data);
                    requestsFinalizadas++;
                    verificarRequestsFinalizadas()
                }
            });
            $.ajax({
                url: '/dados_atendimento_tipo_ocorrencia',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    preencherDadosAtendimento_tipoOcorrencia(data);
                    requestsFinalizadas++
                    verificarRequestsFinalizadas()
                }
            });
            $.ajax({
                url: '/dados_atendimento_por_genero',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    preencherDadosAtendimento_generoSexo(data);
                    requestsFinalizadas++
                    verificarRequestsFinalizadas()
                } 
            });
            $.ajax({
                url:'/dados_atendimento_por_fxEtaria',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    console.log(data)
                    preencherDadosAtendimento_fxEtaria(data);
                    requestsFinalizadas++
                    verificarRequestsFinalizadas()
                }
            });
            $.ajax({
                url: '/dados_atendimento_por_municipio',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    console.log(data)
                    preencherDadosAtendimento_nomeMunicipio(data);
                    requestsFinalizadas++
                    verificarRequestsFinalizadas()
                } 
            });
            $.ajax({
                url: '/dados_atendimento_por_unidade',
                type: 'POST',
                data: {
                    data_inicio: dataInicio,
                    data_fim: dataFim,
                    veiculo: veiculo
                },
                success: function(data) {
                    console.log(data)
                    preencherDadosAtendimento_nomeUnidade(data);
                    requestsFinalizadas++
                    verificarRequestsFinalizadas()
                } 
            });
            $(document).ajaxStop(function() {
                $('#loader').addClass('hidden');
                $('#overlay').addClass('hidden');
            })
        }
        
        function calcularMedia(lista) {
            var soma = lista.reduce((total, num) => total + num, 0);
            return soma / lista.length;
        }
        function preencherDadosAtendimento(data) {
            var tabela = $('#dados_atendimento');
            tabela.empty();

            if (data.length > 0) {
                var total = data.reduce((total_geral, item) => total_geral + item.total_atendimentos, 0);
                var mediaTempoResposta = calcularMedia(data.map(item => item.tempo_medio_resposta_saida_base));
                var mediaTempoResposta_total = calcularMedia(data.map(item => item.tempo_medio_resposta_total));

                var headerRow = '<thead class="thead-dark"><tr><th>Indicadores gerais</th><th>Total do período</th>';
                var totalRow = '<tbody><tr><td>Total Atendimentos</td><td>' + total + '</td>';
                var mediaTempoRespostaSaidaBase = '<tr><td>Tempo Médio da saida da base</td><td>' + converterSegundosParaHoraMinutoSegundo(mediaTempoResposta) + '</td>';
                var mediaTempoRespostaTotal = '<tr><td>Tempo Médio Resposta Total</td><td>' + converterSegundosParaHoraMinutoSegundo(mediaTempoResposta_total) + '</td>';

                data.forEach(function(item) {
                    headerRow += '<th>' + item.mes + '</th>';
                    totalRow += '<td>' + item.total_atendimentos + '</td>';
                    mediaTempoRespostaSaidaBase += '<td>' + converterSegundosParaHoraMinutoSegundo(item.tempo_medio_resposta_saida_base) +  '</td>'
                    mediaTempoRespostaTotal += '<td>' + converterSegundosParaHoraMinutoSegundo(item.tempo_medio_resposta_total) +  '</td>'
                });

                headerRow += '</tr></thead>';
                totalRow += '</tr></tbody>';
                mediaTempoRespostaSaidaBase += '</tr>';

                tabela.append(headerRow);
                tabela.append(totalRow);
                tabela.append(mediaTempoRespostaSaidaBase);
                tabela.append(mediaTempoRespostaTotal);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        }
        function converterSegundosParaHoraMinutoSegundo(segundos) {
            var horas = Math.floor(segundos / 3600);
            var minutos = Math.floor((segundos % 3600) / 60);
            var segundosRestantes = Math.floor(segundos % 60);
            return ('0' + horas).slice(-2) + ':' + ('0' + minutos).slice(-2) + ':' + ('0' + segundosRestantes).slice(-2);
        }
            function preencherDadosAtendimento_tipoOcorrencia(data) {
            var tabela = $('#dados_atendimento_tipo_ocorrencia');
            tabela.empty();

            if (data.length > 0) {
                var groupedData = {}; // Objeto para armazenar os dados agrupados

                // Agrupar os dados por tipo de ocorrência e mês
                data.forEach(function(item) {
                    if (!groupedData[item.nm_tipo_ocorrencia]) {
                        groupedData[item.nm_tipo_ocorrencia] = {};
                        groupedData[item.nm_tipo_ocorrencia]['Total'] = 0; // Adiciona uma propriedade para armazenar o total
                    }
                    if (!groupedData[item.nm_tipo_ocorrencia][item.mes]) {
                        groupedData[item.nm_tipo_ocorrencia][item.mes] = item.total_atendimentos;
                    } else {
                        groupedData[item.nm_tipo_ocorrencia][item.mes] += item.total_atendimentos;
                    }
                    groupedData[item.nm_tipo_ocorrencia]['Total'] += item.total_atendimentos; // Incrementa o total
                });

                // Obter a lista de todos os meses presentes nos dados
                var meses = [];
                data.forEach(function(item) {
                    if (!meses.includes(item.mes)) {
                        meses.push(item.mes);
                    }
                });

                // Preencher a tabela com os dados agrupados
                var headerRow = '<thead class="thead-dark"><tr><th>Tipo de ocorrência</th><th>Total do período</th>'; // Cabeçalho

                // Adicionar os meses como cabeçalho
                meses.forEach(function(mes) {
                    headerRow += '<th>' + mes + '</th>';
                });
                headerRow += '</tr></thead>';

                var totalRow = '<tbody>';

                // Loop sobre cada tipo de ocorrência
                Object.keys(groupedData).forEach(function(tipoOcorrencia) {
                    totalRow += '<tr><td>' + tipoOcorrencia + '</td><td>' + groupedData[tipoOcorrencia]['Total'] + '</td>'; // Nome do tipo de ocorrência e total

                    // Loop sobre cada mês
                    meses.forEach(function(mes) {
                        totalRow += '<td>' + (groupedData[tipoOcorrencia][mes] || 0) + '</td>';
                    });

                    totalRow += '</tr>';
                });

                totalRow += '</tbody>';

                tabela.append(headerRow);
                tabela.append(totalRow);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        }
        function preencherDadosAtendimento_generoSexo(data) {
            var tabela = $('#dados_atendimento_por_genero');
            tabela.empty();

            if (data.length > 0) {
                var groupedData = {}; 

                data.forEach(function(item) {
                    if (!groupedData[item.sexo_vitima]) {
                        groupedData[item.sexo_vitima] = {};
                        groupedData[item.sexo_vitima]['Total'] = 0; // Adiciona uma propriedade para armazenar o total
                    }
                    if (!groupedData[item.sexo_vitima][item.mes]) {
                        groupedData[item.sexo_vitima][item.mes] = item.total_atendimentos;
                    } else {
                        groupedData[item.sexo_vitima][item.mes] += item.total_atendimentos;
                    }
                    groupedData[item.sexo_vitima]['Total'] += item.total_atendimentos;
                });

                var meses = [];
                data.forEach(function(item) {
                    if (!meses.includes(item.mes)) {
                        meses.push(item.mes);
                    }
                });

                var headerRow = '<thead class="thead-dark"><tr><th>Gênero</th><th>Total do período</th>'; 

                meses.forEach(function(mes) {
                    headerRow += '<th>' + mes + '</th>';
                });
                headerRow += '</tr></thead>';

                var totalRow = '<tbody>';
                Object.keys(groupedData).forEach(function(genero) {
                    totalRow += '<tr><td>' + genero + '</td><td>' + groupedData[genero]['Total'] + '</td>'; // genero e total

                    meses.forEach(function(mes) {
                        totalRow += '<td>' + (groupedData[genero][mes] || 0) + '</td>';
                    });

                    totalRow += '</tr>';
                });

                totalRow += '</tbody>';

                tabela.append(headerRow);
                tabela.append(totalRow);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        };
        function preencherDadosAtendimento_fxEtaria(data) {
            var tabela = $('#dados_atendimento_por_fxEtaria');
            tabela.empty();

            if (data.length > 0) {
                var groupedData = {}; // Objeto para armazenar os dados agrupados

                // Agrupar os dados por faixa etaria e mês
                data.forEach(function(item) {
                    if (!groupedData[item.nm_faixa_etaria]) {
                        groupedData[item.nm_faixa_etaria] = {};
                        groupedData[item.nm_faixa_etaria]['Total'] = 0; 
                    }
                    if (!groupedData[item.nm_faixa_etaria][item.mes]) {
                        groupedData[item.nm_faixa_etaria][item.mes] = item.total_atendimentos;
                    } else {
                        groupedData[item.nm_faixa_etaria][item.mes] += item.total_atendimentos;
                    }
                    groupedData[item.nm_faixa_etaria]['Total'] += item.total_atendimentos;
                });

                var meses = [];
                data.forEach(function(item) {
                    if (!meses.includes(item.mes)) {
                        meses.push(item.mes);
                    }
                });

                var headerRow = '<thead class="thead-dark"><tr><th>Faixa etaria</th><th>Total do período</th>'; // Cabeçalho

                meses.forEach(function(mes) {
                    headerRow += '<th>' + mes + '</th>';
                });
                headerRow += '</tr></thead>';

                var totalRow = '<tbody>';
                Object.keys(groupedData).forEach(function(genero) {
                    totalRow += '<tr><td>' + genero + '</td><td>' + groupedData[genero]['Total'] + '</td>'; // faixa etaria e total
                    meses.forEach(function(mes) {
                        totalRow += '<td>' + (groupedData[genero][mes] || 0) + '</td>';
                    });

                    totalRow += '</tr>';
                });

                totalRow += '</tbody>';
                tabela.append(headerRow);
                tabela.append(totalRow);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        };
        function preencherDadosAtendimento_nomeMunicipio(data) {
            var tabela = $('#dados_atendimento_por_municipio');
            tabela.empty();

            if (data.length > 0) {
                var groupedData = {};
                data.forEach(function(item) {
                    if (!groupedData[item.nm_municipio]) {
                        groupedData[item.nm_municipio] = {};
                        groupedData[item.nm_municipio]['Total'] = 0;
                    }
                    if (!groupedData[item.nm_municipio][item.mes]) {
                        groupedData[item.nm_municipio][item.mes] = item.total_atendimentos;
                    } else {
                        groupedData[item.nm_municipio][item.mes] += item.total_atendimentos;
                    }
                    groupedData[item.nm_municipio]['Total'] += item.total_atendimentos; 
                });
                var meses = [];
                data.forEach(function(item) {
                    if (!meses.includes(item.mes)) {
                        meses.push(item.mes);
                    }
                });

                // Preencher a tabela com os dados agrupados
                var headerRow = '<thead class="thead-dark"><tr><th>Município da ocorrência</th><th>Total do período</th>'; // Cabeçalho
                meses.forEach(function(mes) {
                    headerRow += '<th>' + mes + '</th>';
                });
                headerRow += '</tr></thead>';
                var totalRow = '<tbody>';
                Object.keys(groupedData).forEach(function(nomeMunicipio) {
                    totalRow += '<tr><td>' + nomeMunicipio + '</td><td>' + groupedData[nomeMunicipio]['Total'] + '</td>'; // Nome do município e total

                    meses.forEach(function(mes) {
                        totalRow += '<td>' + (groupedData[nomeMunicipio][mes] || 0) + '</td>';
                    });

                    totalRow += '</tr>';
                });

                totalRow += '</tbody>';
                tabela.append(headerRow);
                tabela.append(totalRow);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        }
        function preencherDadosAtendimento_nomeUnidade(data) {
            var tabela = $('#dados_atendimento_por_unidade');
            tabela.empty();

            if (data.length > 0) {
                var groupedData = {};
                data.forEach(function(item) {
                    if (!groupedData[item.nm_unidade_destino]) {
                        groupedData[item.nm_unidade_destino] = {};
                        groupedData[item.nm_unidade_destino]['Total'] = 0;
                    }
                    if (!groupedData[item.nm_unidade_destino][item.mes]) {
                        groupedData[item.nm_unidade_destino][item.mes] = item.total_atendimentos;
                    } else {
                        groupedData[item.nm_unidade_destino][item.mes] += item.total_atendimentos;
                    }
                    groupedData[item.nm_unidade_destino]['Total'] += item.total_atendimentos; 
                });
                var meses = [];
                data.forEach(function(item) {
                    if (!meses.includes(item.mes)) {
                        meses.push(item.mes);
                    }
                });
                var headerRow = '<thead class="thead-dark"><tr><th>Unidade de destino</th><th>Total do período</th>'; 
                meses.forEach(function(mes) {
                    headerRow += '<th>' + mes + '</th>';
                });
                headerRow += '</tr></thead>';

                var totalRow = '<tbody>';
                Object.keys(groupedData).forEach(function(nomeUnidade) {
                    totalRow += '<tr><td>' + nomeUnidade + '</td><td>' + groupedData[nomeUnidade]['Total'] + '</td>'; 
                    meses.forEach(function(mes) {
                        totalRow += '<td>' + (groupedData[nomeUnidade][mes] || 0) + '</td>';
                    });

                    totalRow += '</tr>';
                });

                totalRow += '</tbody>';
                tabela.append(headerRow);
                tabela.append(totalRow);
            } else {
                var mensagemErro = '<tbody><tr><td colspan="1">Nenhum dado disponível</td></tr></tbody>';
                tabela.append(mensagemErro);
            }
        };
        function letraMaiuscula(trocar){
            return trocar.toLowerCase().split(' ').map(palavra => palavra.charAt(0).toUpperCase() + palavra.slice(1)).join(' ');
        }
    });
});