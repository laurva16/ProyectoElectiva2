# reportes.py
# Módulo de gestión de reportes con MongoDB

from flask import Blueprint, request, jsonify, send_file
from functools import wraps
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from database import tickets_collection, peliculas_collection, salas_collection
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Token mal formateado'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token faltante'}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user_data = request.current_user
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403
        return f(*args, **kwargs)
    
    return decorated


# ✅ Función auxiliar para convertir precio a float de forma segura
def convertir_precio(precio):
    """Convierte el precio a float, manejando strings y números"""
    try:
        if isinstance(precio, str):
            # Remover símbolos de moneda y espacios
            precio = precio.replace('$', '').replace(',', '').strip()
        return float(precio)
    except (ValueError, TypeError):
        return 0.0


# Agregar este endpoint al archivo reportes.py después de los imports y antes de los otros endpoints

@reportes_bp.route('/estadisticas-rapidas', methods=['GET'])
@jwt_required
def obtener_estadisticas_rapidas():
    """Obtener estadísticas rápidas para el dashboard - SOLO ADMIN"""
    try:
        # ✅ VERIFICAR QUE SEA ADMIN
        user_data = request.current_user
        if user_data.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Se requieren permisos de administrador'
            }), 403
        
        from datetime import datetime, timedelta
        
        # Fecha de hoy
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # 1. Total de películas (SIN FILTRO DE ESTADO o con el estado correcto)
        # ✅ CAMBIO: Contar TODAS las películas o ajustar el campo
        total_peliculas = peliculas_collection.count_documents({})
        # Si tus películas tienen campo 'activo' boolean: 
        # total_peliculas = peliculas_collection.count_documents({"activo": True})
        
        # 2. Tickets vendidos hoy
        tickets_hoy = tickets_collection.count_documents({
            "fecha_funcion": hoy,
            "estado": {"$in": ["pagado", "reservado"]}
        })
        
        # 3. Ingresos de hoy
        tickets_hoy_data = list(tickets_collection.find({
            "fecha_funcion": hoy,
            "estado": {"$in": ["pagado", "reservado"]}
        }))
        ingresos_hoy = sum(convertir_precio(t.get('precio', 0)) for t in tickets_hoy_data)
        
        # 4. Total de salas
        total_salas = salas_collection.count_documents({})
        
        # 5. Total de usuarios
        try:
            from database import usuarios_collection
            total_usuarios = usuarios_collection.count_documents({})
        except:
            total_usuarios = 0
        
        # 6. Tickets de ayer para comparación
        ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        tickets_ayer = tickets_collection.count_documents({
            "fecha_funcion": ayer,
            "estado": {"$in": ["pagado", "reservado"]}
        })
        
        # Calcular porcentaje de cambio vs ayer
        if tickets_ayer > 0:
            cambio_tickets = ((tickets_hoy - tickets_ayer) / tickets_ayer) * 100
        else:
            cambio_tickets = 100 if tickets_hoy > 0 else 0
        
        # ✅ LOG PARA DEBUG
        print(f"DEBUG Estadísticas:")
        print(f"- Total películas: {total_peliculas}")
        print(f"- Tickets hoy: {tickets_hoy}")
        print(f"- Ingresos hoy: {ingresos_hoy}")
        print(f"- Total salas: {total_salas}")
        
        return jsonify({
            'success': True,
            'data': {
                'total_peliculas': total_peliculas,
                'tickets_vendidos_hoy': tickets_hoy,
                'ingresos_hoy': round(ingresos_hoy, 2),
                'total_salas': total_salas,
                'total_usuarios': total_usuarios,
                'cambio_tickets': round(cambio_tickets, 2),
                'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        print(f"Error en estadisticas_rapidas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500

@reportes_bp.route('/ventas', methods=['GET'])
@admin_required
def generar_reporte_ventas():
    """Generar reporte de ventas en JSON"""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Construir filtro
        filtro = {"estado": {"$in": ["pagado", "reservado"]}}
        
        if fecha_inicio:
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$gte'] = fecha_inicio
        
        if fecha_fin:
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$lte'] = fecha_fin
        
        # Obtener tickets
        tickets = list(tickets_collection.find(filtro))
        for t in tickets:
            t['_id'] = str(t['_id'])
        
        # ✅ Calcular estadísticas con conversión de tipos
        total_tickets = len(tickets)
        ingresos_totales = sum(convertir_precio(t.get('precio', 0)) for t in tickets)
        
        # Ventas por película
        ventas_pelicula = {}
        for t in tickets:
            pelicula = t.get('pelicula_nombre', 'Desconocida')
            if pelicula not in ventas_pelicula:
                ventas_pelicula[pelicula] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_pelicula[pelicula]['cantidad'] += 1
            ventas_pelicula[pelicula]['ingresos'] += convertir_precio(t.get('precio', 0))
        
        # Ventas por sala
        ventas_sala = {}
        for t in tickets:
            sala = t.get('sala_nombre', 'Desconocida')
            if sala not in ventas_sala:
                ventas_sala[sala] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_sala[sala]['cantidad'] += 1
            ventas_sala[sala]['ingresos'] += convertir_precio(t.get('precio', 0))
        
        # ✅ Redondear ingresos en las ventas por película y sala
        for pelicula in ventas_pelicula:
            ventas_pelicula[pelicula]['ingresos'] = round(ventas_pelicula[pelicula]['ingresos'], 2)
        
        for sala in ventas_sala:
            ventas_sala[sala]['ingresos'] = round(ventas_sala[sala]['ingresos'], 2)
        
        return jsonify({
            'success': True,
            'message': 'Reporte generado exitosamente',
            'data': {
                'resumen': {
                    'total_tickets': total_tickets,
                    'ingresos_totales': round(ingresos_totales, 2),
                    'fecha_inicio': fecha_inicio or 'Todas',
                    'fecha_fin': fecha_fin or 'Todas'
                },
                'ventas_por_pelicula': ventas_pelicula,
                'ventas_por_sala': ventas_sala,
                'tickets': tickets
            }
        }), 200
        
    except Exception as e:
        print(f"Error en generar_reporte_ventas: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500


# reportes.py - SOLUCIÓN COMPLETA PARA PDF

@reportes_bp.route('/ventas/pdf', methods=['GET'])
@admin_required
def generar_reporte_ventas_pdf():
    """Generar reporte de ventas en PDF - VERSIÓN CORREGIDA"""
    try:
        fecha_inicio = request.args.get('fecha_inicio', 'Todas')
        fecha_fin = request.args.get('fecha_fin', 'Todas')
        
        # Construir filtro
        filtro = {"estado": {"$in": ["pagado", "reservado"]}}
        
        if fecha_inicio != 'Todas':
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$gte'] = fecha_inicio
        
        if fecha_fin != 'Todas':
            if 'fecha_funcion' not in filtro:
                filtro['fecha_funcion'] = {}
            filtro['fecha_funcion']['$lte'] = fecha_fin
        
        # ✅ Obtener tickets
        tickets = list(tickets_collection.find(filtro))
        
        print(f"\n{'='*60}")
        print(f"📊 GENERANDO REPORTE PDF")
        print(f"{'='*60}")
        print(f"Período: {fecha_inicio} a {fecha_fin}")
        print(f"Total tickets encontrados: {len(tickets)}")
        
        # ✅ Enriquecer datos de tickets
        for ticket in tickets:
            # Asegurar que tenga pelicula_nombre
            if not ticket.get('pelicula_nombre'):
                if ticket.get('pelicula_id'):
                    pelicula = peliculas_collection.find_one({'id': ticket['pelicula_id']})
                    ticket['pelicula_nombre'] = pelicula['titulo'] if pelicula else 'Película no encontrada'
                else:
                    ticket['pelicula_nombre'] = 'Sin información'
            
            # Asegurar que tenga sala_nombre
            if not ticket.get('sala_nombre'):
                if ticket.get('sala_id'):
                    sala = salas_collection.find_one({'id': ticket['sala_id']})
                    ticket['sala_nombre'] = sala['nombre'] if sala else 'Sala no encontrada'
                else:
                    ticket['sala_nombre'] = 'Sin información'
            
            # Asegurar que el precio sea numérico
            if 'precio' in ticket:
                ticket['precio'] = convertir_precio(ticket['precio'])
        
        if tickets:
            print(f"\n📌 Ejemplo de ticket procesado:")
            ejemplo = tickets[0]
            print(f"   - Película: {ejemplo.get('pelicula_nombre', 'N/A')}")
            print(f"   - Sala: {ejemplo.get('sala_nombre', 'N/A')}")
            print(f"   - Precio: ${ejemplo.get('precio', 0)}")
            print(f"   - Fecha: {ejemplo.get('fecha_funcion', 'N/A')}")
        
        # ✅ Calcular estadísticas
        total_tickets = len(tickets)
        ingresos_totales = sum(t.get('precio', 0) for t in tickets)
        
        # ✅ Ventas por película
        ventas_pelicula = {}
        for t in tickets:
            pelicula = t.get('pelicula_nombre', 'Desconocida')
            if pelicula not in ventas_pelicula:
                ventas_pelicula[pelicula] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_pelicula[pelicula]['cantidad'] += 1
            ventas_pelicula[pelicula]['ingresos'] += t.get('precio', 0)
        
        # ✅ Ventas por sala
        ventas_sala = {}
        for t in tickets:
            sala = t.get('sala_nombre', 'Desconocida')
            if sala not in ventas_sala:
                ventas_sala[sala] = {'cantidad': 0, 'ingresos': 0.0}
            ventas_sala[sala]['cantidad'] += 1
            ventas_sala[sala]['ingresos'] += t.get('precio', 0)
        
        print(f"\n💰 Resumen calculado:")
        print(f"   - Ingresos totales: ${ingresos_totales:,.2f}")
        print(f"   - Películas únicas: {len(ventas_pelicula)}")
        print(f"   - Salas únicas: {len(ventas_sala)}")
        
        if ventas_pelicula:
            print(f"\n🎬 Top 3 películas por ingresos:")
            top_peliculas = sorted(ventas_pelicula.items(), key=lambda x: x[1]['ingresos'], reverse=True)[:3]
            for i, (nombre, datos) in enumerate(top_peliculas, 1):
                print(f"   {i}. {nombre}: ${datos['ingresos']:,.2f} ({datos['cantidad']} tickets)")
        
        print(f"{'='*60}\n")
        
        # ========================
        # GENERAR PDF
        # ========================
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        # Título principal
        story.append(Paragraph("🎬 CineMax - Reporte de Ventas", titulo_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Información del reporte
        info_data = [
            ['📅 Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['📆 Período:', f'{fecha_inicio} hasta {fecha_fin}'],
            ['👤 Generado por:', request.current_user.get('email', 'N/A')],
            ['📊 Total de registros:', str(total_tickets)]
        ]
        
        info_table = Table(info_data, colWidths=[2.2*inch, 4.3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1'))
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.25*inch))
        
        # ========================
        # RESUMEN EJECUTIVO
        # ========================
        story.append(Paragraph("💼 Resumen Ejecutivo", subtitulo_style))
        
        precio_promedio = (ingresos_totales / total_tickets) if total_tickets > 0 else 0
        
        resumen_data = [
            ['Métrica', 'Valor'],
            ['🎟️ Total de Tickets Vendidos', str(total_tickets)],
            ['💵 Ingresos Totales', f'${ingresos_totales:,.2f} COP'],
            ['📊 Precio Promedio por Ticket', f'${precio_promedio:,.2f} COP']
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3.5*inch, 2.5*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        story.append(resumen_table)
        story.append(Spacer(1, 0.25*inch))
        
        # ========================
        # VENTAS POR PELÍCULA
        # ========================
        story.append(Paragraph("🎬 Ventas por Película", subtitulo_style))
        
        if ventas_pelicula:
            pelicula_data = [['Película', 'Tickets', 'Ingresos', '% Total']]
            
            for pelicula, datos in sorted(ventas_pelicula.items(), key=lambda x: x[1]['ingresos'], reverse=True):
                porcentaje = (datos['ingresos'] / ingresos_totales * 100) if ingresos_totales > 0 else 0
                nombre_corto = pelicula[:35] + '...' if len(pelicula) > 35 else pelicula
                pelicula_data.append([
                    nombre_corto,
                    str(datos['cantidad']),
                    f"${datos['ingresos']:,.2f}",
                    f"{porcentaje:.1f}%"
                ])
        else:
            pelicula_data = [
                ['Película', 'Tickets', 'Ingresos', '% Total'],
                ['Sin datos de ventas en el período', '0', '$0.00', '0%']
            ]
        
        pelicula_table = Table(pelicula_data, colWidths=[2.8*inch, 1*inch, 1.5*inch, 0.8*inch])
        pelicula_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')])
        ]))
        
        story.append(pelicula_table)
        story.append(Spacer(1, 0.25*inch))
        
        # ========================
        # VENTAS POR SALA
        # ========================
        story.append(Paragraph("🎭 Ventas por Sala", subtitulo_style))
        
        if ventas_sala:
            sala_data = [['Sala', 'Tickets', 'Ingresos', '% Total']]
            
            for sala, datos in sorted(ventas_sala.items(), key=lambda x: x[1]['ingresos'], reverse=True):
                porcentaje = (datos['ingresos'] / ingresos_totales * 100) if ingresos_totales > 0 else 0
                sala_data.append([
                    sala,
                    str(datos['cantidad']),
                    f"${datos['ingresos']:,.2f}",
                    f"{porcentaje:.1f}%"
                ])
        else:
            sala_data = [
                ['Sala', 'Tickets', 'Ingresos', '% Total'],
                ['Sin datos de ventas en el período', '0', '$0.00', '0%']
            ]
        
        sala_table = Table(sala_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 0.8*inch])
        sala_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
        ]))
        
        story.append(sala_table)
        
        # ========================
        # NOTA SI NO HAY DATOS
        # ========================
        if not tickets:
            story.append(Spacer(1, 0.3*inch))
            advertencia_style = ParagraphStyle(
                'Warning',
                parent=styles['Normal'],
                textColor=colors.HexColor('#dc2626'),
                fontSize=11,
                alignment=TA_CENTER
            )
            advertencia = Paragraph(
                "⚠️ <b>Nota:</b> No se encontraron tickets vendidos en el período seleccionado.",
                advertencia_style
            )
            story.append(advertencia)
        
        # ========================
        # PIE DE PÁGINA
        # ========================
        story.append(Spacer(1, 0.4*inch))
        pie_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        pie = Paragraph(
            f"Reporte generado por CineMax System - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            pie_style
        )
        story.append(pie)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        print(f"✅ PDF generado exitosamente: {filename}\n")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"\n❌ ERROR AL GENERAR PDF:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        
        return jsonify({
            'success': False,
            'message': f'Error al generar PDF: {str(e)}'
        }), 500

@reportes_bp.route('/ocupacion', methods=['GET'])
@admin_required
def generar_reporte_ocupacion():
    """Generar reporte de ocupación de salas"""
    try:
        fecha = request.args.get('fecha')
        
        if not fecha:
            return jsonify({
                'success': False,
                'message': 'La fecha es requerida'
            }), 400
        
        # Obtener todas las salas
        salas = list(salas_collection.find())
        
        reporte = []
        for sala in salas:
            # Contar tickets vendidos para esa sala en esa fecha
            tickets_vendidos = tickets_collection.count_documents({
                "sala_id": sala['id'],
                "fecha_funcion": fecha,
                "estado": {"$in": ["pagado", "reservado"]}
            })
            
            capacidad = sala['capacidad']
            ocupacion = (tickets_vendidos / capacidad * 100) if capacidad > 0 else 0
            
            reporte.append({
                'sala': sala['nombre'],
                'capacidad': capacidad,
                'tickets_vendidos': tickets_vendidos,
                'asientos_disponibles': capacidad - tickets_vendidos,
                'porcentaje_ocupacion': round(ocupacion, 2)
            })
        
        return jsonify({
            'success': True,
            'message': 'Reporte de ocupación generado',
            'data': {
                'fecha': fecha,
                'salas': reporte
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500